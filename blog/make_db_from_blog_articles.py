#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# このスクリプトは ume2509 アカウント専用。
# 理由: fc2blog と /c/my_prog/docusaurus/github_page/blog のデータを統合した DB を既に ouchaku_db_path に格納済みであることを前提にしている。
# 
#
# 実行方法：
# 1. conda activate docusaurus
# 2. Git-bash 端末から `./make_db_from_blog_articles.py`
#
# 確認方法:
#   GUI ツール 'DB Browser for SQLite' で閲覧。
#   read-only モードとする。
#
# 目的：
# 1. ume2509/blog ディレクトリの *.md, *.mdx の内容をデータベースに登録する。
#  既存の統合データベース（＝FC2Blog の全データ ＋ 2024-06 から 2025-08 までの ouchaku blog のデータを格納した DB）は、既に ume2509/blog/_ouchaku_fc2/base.db に作成済み。
# 2. そのデータベースに登録が終わった時点で、データベースの内容をテキストファイル（_db_out.text）に書き出す。
#
# 処理：
# 1. ume2509/blog/_ouchaku_fc2/base.db は 「fc2.db のデータを docusaurus のテーブル形式に合わせて変換したもの」に ouchaku/blog の全記事を追加したもの。
# 2. _ouchaku_fc2/base.db をコピーして /blog/_ds_blog.db とする。
# 4. /blog/*.md と /blog/*.mdx の内容を /blog/_ds_blog.db に追加する。差分を追加したり、日時を見て追加するのではなく、毎回、新たに全ての md, mdx ファイルを追加する。差分確認の手間とさして変わらない筈なので。
#
# 残件：
# [ ] tags から個別に tag を抽出
# [ ] 輝度パラメータの -outfile でデータベース（/blog/_ds_blog.db）の内容を、/blog/_all_data.text に出力する。そのファイルを Emacs/vi で検索するため。
# [ ] /blog の他に /docs 以下のカテゴリーの記事もデータベースに格納すること。
#
#
# 履歴：
# 2025-09-05 ume2509 に合わせて変更した。
# 2024-08-06 テキストファイル出力の書式を微修正
# 2024-08-04 データベース（_ds_blog.db）の内容をテキストファイル（_db_out.text）に書き出す機能を追加開始。
# 2024-07-31 Logger を組み込んだ。データベースに格納する URL を GitHub pages の完全パスに変更。
# 2024-07-28 説明文追加
# 2024-07-15 機能追加。
# 2024-07-14 作成。ChatGPT-4o に作らせた。
#
#
# 以下は ChatGPT-4o で作成した時のプロンプト
#---
# Windows11 + Python3 で以下の仕様のスクリプトを作成して。
#
# カレント・ディレクトリをスキャンして拡張子が ".md" と ".mdx" の markdown ファイルを対象にして、それぞれのファイルについて以下の処理をします。サブディレクトリは全て無視します。
#
# 1. ファイル名が YYYY-MM-DD-title.md （例: "2024-07-10-a_article.md"）もしくは YYYY-MM-DD-title.mdx （例： "2011-9-10-other_article.mdx"）だけを処理の対象とします。それに合致しないファイルは無視します。
#
# 2. 1 で合致したファイル名を昇順にソートした後に順次、以下の処理を行います。
#
# 3. ファイルを読み込み、最初の "# " で始まる行、つまり markdown の 「H1 見出し」に相当する行の文字列を 変数 title に格納にます。
#
# 例："2024-07-10-a_article.md" の冒頭部分が以下の場合、変数 title には "主な経済指標の推移" を代入します。
#
# ```2024-07-10-a_article.md
# ---
# this is front matter
# this is front matter
# ---
#
# # 主な経済指標の推移
#
# 最近の経済動向を…
#
# ```
#
# 4. ファイルの内容を全て読み出し、変数 body に代入します。
#
# 5. ファイル名の冒頭、10文字を 変数 date_create に代入します。
# 例： "2024-07-10-a_article.md" ならば、"2024-07-10" を変数 date_create に代入します。
#
# 6. （explore で見たときの）ファイルの更新日時を参照して "2024-07-13 11:23" といった日時データを変数 date_update に代入します。
#
# 7. ファイル名から以下のように文字列を構成して、変数 url に代入します。
# 例：ファイル名が "2024-07-10-a_article.md" ならば、"/blog/2024/07/10/a_article" を変数 date_create に代入します。
#
# 8. 変数の title, body, date_create, date_update, url に代入を終えた段階で、ダミー関数 sql_add_record(id, url, title, date_create, date_update, body) を呼び出します。 id は上記の 2移行のループの整数カウントです。
#
#
#
# ------------------------
#
# 以下のPythonスクリプトは、指定された仕様に従ってカレントディレクトリ内の`.md`および`.mdx`ファイルを処理します。このスクリプトは、指定された条件に合致するファイルを昇順にソートし、それぞれのファイルの必要なデータを抽出してダミー関数`sql_add_record`を呼び出します。


import os
import re
import sys
import sqlite3
import shutil
from datetime import datetime

from logging import (
    getLogger,
    StreamHandler,
    FileHandler,
    Formatter,
    basicConfig,
    DEBUG,
    INFO,
    CRITICAL,
    ERROR,
    WARNING,
    NOTSET,
)


"""
済：

1. _ouchaku_fc2/base.db をコピーして blog/_ds_blog.db とすること
3. その _ds_blog.db に docusaurus/ume2509/blog データを追加する。
"""

# TODO: PyQt5 で GUI 化。
# TODO: front matter の解析
# TODO: 複数タグの処理
# TODO: カテゴリーなどを GUI ツールで付与できるように

class Gd:
    """グローバル・データ
    """
    db_path: str = "_ds_blog.db"
    basedb_path: str = "./_ouchaku_fc2/base.db"
    err_count: int = 0
    warn_count: int = 0
    emp_count: int = 0  # 当該 url の記事が空だった件数
    img_dir: str = "img"



def init_db()-> sqlite3.Connection:
    """ DBの初期化
    使わない。
    """
    do_create: bool = False
    if not os.path.exists(Gd.db_path):
        do_create = True

    db: sqlite3.Connection = sqlite3.connect(Gd.db_path)

    if do_create:
        sql = """create table ds_blog(
                    id integer primary key,
                    url_no int UNIQUE ON CONFLICT REPLACE,
                    url text,
                    title text,
                    body text,
                    body_untag text,
                    body_bk text,
                    category text,
                    date_create text,
                    date_update text,
                    tags text,
                    comment text,
                    spair1 text,
                    del_mark int)
            """
        db.execute(sql)

    return db


def copy_ouchaku_db():
    """
    凍結 DB データ（ouchaku+FC2blog が格納された DB データ）を Gd.basedb_path から読み込む。
    以下の手順で db_path を作成する。
    1. basedb をコピーして db_path とする。
    3. db_path を SQLite で開いて、ハンドルを返す
    """

    if not os.path.isfile(Gd.basedb_path):
        # basedb ファイルが無い
        print(f"### There is no {Gd.basedb_path} file.\n")
        sys.exit(1)

    # コピーして db とする。
    shutil.copy(Gd.basedb_path, Gd.db_path)

    # db_path を開いてハンドルを返す。
    db: sqlite3.Connection = sqlite3.connect(Gd.db_path)
    return db



def sql_add_record(db, id, url, title, body, date_create, date_update="", category="", fr_mt="", comment=""):
    #
    sql: str = "REPLACE INTO ds_blog (id, url, title, body, date_create, date_update, category, fr_mt, comment) VALUES(?,?,?,?,?,?,?,?,?)"
    db.execute(sql, (id, url, title, body, date_create, date_update, category, fr_mt, comment))
    db.commit()


def scan_md_files_and_add_records():
    """ 現在の /blog ディレクトリ内のファイルをスキャンして SQL に追加
    """
    # TODO: tags の内容を個別に抽出
    # TODO: front matter の開始と終了を '---' から正規表現の '^---.*$' にする。つまり上位互換に。

    current_directory = os.getcwd()
    files = [f for f in os.listdir(current_directory) if os.path.isfile(os.path.join(current_directory, f))]

    # ".md" と ".mdx" ファイルをフィルタリングし、指定された形式のファイル名のみを残す
    md_files = [f for f in files if re.match(r'\d{4}-\d{2}-\d{2}-.+\.mdx?$', f)]

    # ファイル名を昇順にソート
    md_files.sort()

    db = copy_ouchaku_db()  # ouchaku + fc2 の凍結データを転送

    # 各ファイルを処理
    # fc2blog の id は 1..22464 の範囲、ouchaku は 30000 からなので docusaurus の blog は 32000 からとする。
    for id, filename in enumerate(md_files, 32000):
        file_path = os.path.join(current_directory, filename)

        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # front matter, title, body を抽出
        fr_mt = ""
        body = ""
        title = ""
        is_front_matter = False

        phase = "begin"

        for line in lines:
            match phase:
                case "begin":
                    if line.strip() == "---" :
                        phase = "fm_begin"
                    elif line.startswith("# ") :
                        title = line[2:].strip()
                        phase = "title"
                case "fm_begin":
                    if line.strip() == "---" :
                        phase = "fm_end"
                    else:
                        fr_mt += line
                case "fm_end":
                    if line.startswith("# ") :
                        title = line[2:].strip()
                        phase = "title"
                case "title":
                    if not line.isspace():
                    #if not line.strip() :
                        phase = "body"
                        body += line
                case "body":
                    body += line
                case _:
                    raise Exception("ありえないmatch分岐")
        """
        for line in lines:
            if line.strip() == "---" and not is_front_matter:
                is_front_matter = True
                continue
            elif line.strip() == "---" and is_front_matter:
                is_front_matter = False
                continue

            if is_front_matter:
                fr_mt += line
            else:
                if title : # タイトル前の行、タイトル行の後の空白行は無視
                    body += line
                if line.startswith("# ") and not title:
                    # body += line 
                    title = line[2:].strip()
        """

        category = ""

        # ファイルの作成日、更新日時を取得
        date_create = filename[:10]
        date_update = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')

        # URLを生成
        # 具体例：
        #   https://ume2509.github.io/ds/blog/2025/09/04/ja_lec
        url = f"https://ume2509.github.io/ds/blog/{date_create.replace('-', '/')}/{filename[11:].rsplit('.', 1)[0]}"

        # sql_add_recordを呼び出す
        sql_add_record(db, id, url, title, body, date_create, date_update, category, fr_mt, "")

    # DB 終了処理
    db.close()


def db_fileout():

    logger = get_logger()
    logger.info("start...")
    db: sqlite3.Connection = sqlite3.connect(Gd.db_path)

    dump_file = "_db_out.text"
    fout = open(dump_file, mode="w", encoding="utf-8")

    if not os.path.exists(Gd.db_path):
        print("*** Error! no db\n")
        print("*** Error! no db\n", file=sys.stderr)
        logger.error("*** Error! no db\n")
        Gd.err_count += 1
        return

    no = 0

    db = sqlite3.connect(Gd.db_path)

    cur = db.cursor()
    sql = "SELECT id, url, title, body, date_create, date_update, category, comment FROM ds_blog ORDER BY id"
    for row in cur.execute(sql):
        no += 1
        print(
            f'id:{row[0]:>7d}: ({row[6]})\n<a href="{row[1]}" target="_blank">{row[2]}</a> ({row[4]})\n\n{row[3]}\n{row[4]}\n{row[5]}\n{row[7]}\n', file=fout)
        print("-------------------------", file=fout)

    fout.close()
    # DB 終了処理
    db.close()
    logger.info("end...")


def get_logger():
    """ロガー用シングルトンを返す"""
    return getLogger(__name__)


def set_logger():
    """ロガーの設定"""
    log_filename = "_log_make_db_from_blog_artiles.text"
    log_format = "%(levelname)-9s %(asctime)s [%(funcName)-16s]:%(message)s"
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    try:
        # ファイルハンドラーを作成してロガーに追加
        file_handler = FileHandler(filename=log_filename, encoding="utf-8", mode="w")
        file_handler.setLevel(DEBUG)  # ファイルハンドラーのログレベルを設定
        file_formatter = Formatter(log_format, datefmt="%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Failed to set file hander:{e}")

    # コンソールハンドラーを作成してロガーに追加。コンソールに出力するStreamHandlerを利用
    console_handler = StreamHandler()
    console_handler.setLevel(DEBUG)  # コンソールハンドラーのログレベルを設定
    console_formatter = Formatter(log_format, datefmt="%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.propagate = False
    logger.info("Logger start...")
    return logger

# --------------------
if __name__ == "__main__":
    # Gd.db_path のファイルが存在すれば削除
    if os.path.isfile(Gd.db_path):
        os.remove(Gd.db_path)

    # blog 記事をデータベースに追加
    scan_md_files_and_add_records()

    # データベースの内容をテキストファイルに書き出す
    db_fileout()
