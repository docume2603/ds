#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 目的：
#   Dodusaurus 用。以下の問題を回避するためのスクリプト。
#   このスクリプトを bash スクリプトの中で実行させ、その後に
#   git add や git commit, npm run build などを行う。
#
# 実行方法：
#  1. cd /c/my_prog/docusaurus/github_page
#  2. python solv_pseudo_symlink.py
#
# 返り値：
#   0 : 正常終了
#   1 : エラー（コピー元のファイルが存在しなかったなど）
#
# 問題：
# Docusaurus はシンボリックリンクがうまく扱えない。
# 少なくとも windows11 環境では /blog/ の下の md ファイルを
# docs/UFO/ にシンボリックリンクさせると、build してブラウザ
# でみると、タイトル（最初の # 見出し 相当）が欠落する。
# このため、blog 用に作成した markdown 記事を UFO のカテゴリー
# の記事としてシンボリックリンクによって流用することができない。
#
# 対処：
# 擬似的にファイルパスの '.', '/'をそれぞれ "@p", "@s" で置き換えた、
# 疑似リンク用のファイルを作成し、
# この python スクリプトで対応するファイルを上書きコピーする。
#
# 例：
# "touch _sylk_@p@p@s@p@p@sblog@s2024-07-30-a_file.md"
# をたとえば docs/UFO/ の下に作成することで、
# ../../blog/2024-07-030_a_file.md
# を docs/UFO/ の下に上書きコピーする。
#
# 履歴：
# 2024-08-06
#     1. "__syln_" というヘッダーで何度も書き間違いが起きたので "_link_" も許容する。
#     2. "@p@p@s@p@p@sblog@s" が長いので、"@blog@" で代用可能にする。
# 2024-07-11 作成。ChatGPT-4o に作らせたが、そのままでは
#   動かなかったので一部のバグを修正。
#

import os
import shutil
import sys

def decode_path(encoded_path):
    if encoded_path.startswith('@blog@'):
        return encoded_path.replace('@blog@', '../../blog/')
    else:
        return encoded_path.replace('@p', '.').replace('@s', '/')

def process_sylk_files(base_dir):
    # print(f'{base_dir=}')
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith('_sylk_') or file.startswith('_link_'):
                # プレフィックスを除去してエンコードされたパスを取得
                encoded_path = file[len('_sylk_'):]
                # デコードして相対パスを取得
                target_path = decode_path(encoded_path)
                target_path_full = os.path.abspath(os.path.join(root, target_path))
                # print(f'{root=},{dirs=}, {target_path=}, {target_path_full=}')
                if os.path.exists(target_path_full):
                    destination_path = os.path.join(root, os.path.basename(target_path))
                    # print(f'{destination_path=}')
                    # 元のファイルを指定されたディレクトリにコピー
                    shutil.copy(target_path_full, destination_path)
                    print(f'Copied {target_path_full} to\n    → {destination_path}')
                else:
                    print(f'Target file does not exist: {target_path_full}')
                    sys.exit(1)  # エラーで終了


if __name__ == "__main__":
    current_dir = os.getcwd()
    process_sylk_files(current_dir)
    sys.exit(0) # 正常終了
