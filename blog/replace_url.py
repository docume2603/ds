#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 履歴：
# 2025-09-04 ouchaku --> ume2509 に変更
# 2025-07-15 Gemini 2.5 Pro で作成

import argparse
import re
import shutil
import sys
from pathlib import Path

# --- 定数 ---
# 置換対象のURLプレフィックス
TARGET_URL_PREFIX = "https://ume2509.github.io/ds/blog/"

# 置換対象を検出するための正規表現パターン
# 形式: <a href="<TARGET_URL_PREFIX><YYYY>/<MM>/<DD>/<slug>" target="_blank"><text></a>
# グループ: (1:YYYY) (2:MM) (3:DD) (4:slug) (5:text)
URL_PATTERN = re.compile(
    rf'<a href="{re.escape(TARGET_URL_PREFIX)}(\d{{4}})/(\d{{2}})/(\d{{2}})/([^"]+)" target="_blank">([^<]+)</a>'
)


def create_replacement_string(match: re.Match) -> str:
    """
    正規表現のマッチオブジェクトから、置換後のMarkdownリンク文字列を生成します。
    """
    year, month, day, slug, text = match.groups()
    # 新しいファイル名形式: YYYY-MM-DD-slug.md
    new_filename = f"{year}-{month}-{day}-{slug}.md"
    # Markdownリンク形式: [text](new_filename)
    return f"[{text}]({new_filename})　"


def process_file(file_path: Path, verify: bool) -> bool:
    """
    指定された単一のMarkdownファイルを処理します。

    - 対象URLを検索し、置換候補を作成します。
    - `-v`オプションが有効な場合、ユーザーに変換内容の確認を求めます。
    - 変換が実行される場合、ファイルのバックアップを作成してから上書き保存します。

    Args:
        file_path: 処理対象のファイルパス (Pathオブジェクト)。
        verify: Trueの場合、置換前にユーザーに確認を求めます。

    Returns:
        処理が正常に完了した場合はTrue、エラーまたはキャンセルされた場合はFalseを返します。
    """
    # 拡張子チェック
    if file_path.suffix.lower() not in ['.md', '.mdx']:
        print(f"エラー: {file_path.name} はサポートされていない拡張子です（.md または .mdx のみ）。", file=sys.stderr)
        return False

    try:
        # ファイルの内容をUTF-8で読み込み
        original_content = file_path.read_text(encoding='utf-8')

        # 正規表現に一致する箇所をすべて検索
        matches = list(URL_PATTERN.finditer(original_content))

        # 一致する箇所がなければ処理終了
        if not matches:
            return True # 変換対象なしは正常な状態

        print(f"ファイル '{file_path.name}' で {len(matches)} 個の変換候補が見つかりました。")

        # 置換リストを作成 (変換前の完全な文字列, 変換後の文字列)
        replacements = []
        for match in matches:
            original_str = match.group(0)
            new_str = create_replacement_string(match)
            replacements.append((original_str, new_str))

        # --verify オプションが指定されている場合の処理
        if verify:
            for i, (original, new) in enumerate(replacements, 1):
                print(f"\n--- 変換候補 {i}/{len(replacements)} in {file_path.name} ---")
                print(f"  変換前: {original}")
                print(f"  変換後: {new}")

            try:
                # ユーザーに実行確認を求める（EnterキーのみでYes）
                answer = input("\n上記の変換を実行しますか？ (Y/n): ").strip().lower()
            except EOFError:  # パイプ処理などで入力がない場合
                answer = 'n'

            if answer not in ('y', 'yes', ''):
                print("変換はキャンセルされました。")
                return True # キャンセルも正常な終了として扱う

        # バックアップファイルの作成 (例: some.md -> some.md_bk)
        # 既存のバックアップファイルは上書きされる
        backup_path = file_path.with_suffix(file_path.suffix + '_bk')
        try:
            shutil.copy(file_path, backup_path)
            print(f"バックアップを作成しました: {backup_path.name}")
        except Exception as e:
            print(f"エラー: バックアップファイルの作成に失敗しました。 {e}", file=sys.stderr)
            return False

        # 内容の置換を実行
        new_content = original_content
        for original, new in replacements:
            new_content = new_content.replace(original, new, 1)

        # 変換後の内容でファイルを上書き
        file_path.write_text(new_content, encoding='utf-8')
        print(f"ファイルを更新しました: {file_path.name}")
        return True

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {file_path}", file=sys.stderr)
        return False
    except IOError as e:
        print(f"エラー: ファイルの読み書き中にエラーが発生しました: {file_path}\n{e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {file_path}\n{e}", file=sys.stderr)
        return False


def main():
    """
    コマンドライン引数を解析し、各ファイルに対して置換処理を実行します。
    """
    parser = argparse.ArgumentParser(
        prog="replace_url.py",
        description="Markdownファイル内の特定の<a>タグをMarkdown形式のローカルリンクに置換します。",
        epilog=(
            "使用例:\n"
            "  python replace_url.py file1.md file2.mdx\n"
            "  python replace_url.py *.md --verify"
        ),
        formatter_class=argparse.RawTextHelpFormatter # ヘルプメッセージの改行を維持
    )

    parser.add_argument(
        'files',
        nargs='*',  # 0個以上のファイル引数を許容
        metavar='FILE',
        help='処理対象のMarkdownファイル（.md, .mdx）。\nGit-bashなどではワイルドカードも利用可能です。'
    )

    parser.add_argument(
        '-v', '--verify',
        action='store_true',
        help='置換を実行する前に、変更内容を表示して確認を求めます。'
    )

    args = parser.parse_args()

    # ファイルが一つも指定されなかった場合はヘルプを表示して終了
    if not args.files:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # 全体の処理結果を追跡するためのフラグ
    has_error = False

    for file_str in args.files:
        file_path = Path(file_str)
        if not process_file(file_path, args.verify):
            has_error = True  # 1つでも処理に失敗したらエラーフラグを立てる

    # print("\nすべての処理が完了しました。")
    sys.exit(1 if has_error else 0)


if __name__ == '__main__':
    main()
