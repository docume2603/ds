#!/usr/bin/env python
# -*- coding: utf-8 -*-

r"""
md_2astr_wrapper.py

複数の Markdown ファイルに対して、ゼロ幅非接合子 (U+200C) を用いた ** マーカーのラップ
およびバックアップ作成を行うコマンドラインツール。

使い方:
  md_2astr_wrapper.py [-h] file [file ...]

  file              処理対象の Markdown ファイル (拡張子 .md/.mdx 推奨)

オプション:
  -h, --help        このヘルプメッセージを表示して終了

処理内容:
  1. <file> のコピーを <file>_bk に作成
  2. <file> を UTF-8 で読み込み
  3. 全ての "**" の前後にゼロ幅非接合子を挿入
  4. <file> に UTF-8 で上書き出力

複数ファイルを指定すると、順に処理を行います。
どれか一つでエラーが生じた場合、そのファイル名を stderr に出力し、即時終了します。


履歴：
2025-08-12 一部修正

"""
import argparse
import sys
import os
import shutil
import re

ZWNJ = '\u200C'
PLAIN = '**'
WRAPPED = f'{ZWNJ}{PLAIN}{ZWNJ}'


# === 変換除外リスト（basename+拡張子） ===
IGNORE_LIST = ['2025-07-14-hack_ai_generated_md_text.md', 'skip_this.md', 'ignore_sample.mdx']

def wrap_zwnj_once(text: str) -> str:

    # r'\*\*' を r'**' に置換
    text = re.sub(r'\\\*\\\*', r'**', text)

    # 既に ZWNJ に囲まれていない ** のみをラップ
    pattern = re.compile(rf'(?<!{ZWNJ}){re.escape(PLAIN)}(?!{ZWNJ})')
    return pattern.sub(WRAPPED, text)


def process_file(path: str) -> None:
    # バックアップを作成
    bak = path + '_bk'
    shutil.copy2(path, bak)

    # ファイル読み込み
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # マーカーをラップ
    result = wrap_zwnj_once(raw)

    # 上書き出力
    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)


def main():
    parser = argparse.ArgumentParser(
        description='Wrap Markdown ** markers with ZWNJ and backup originals',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'files', nargs='+', help='Markdown files to process'
    )
    args = parser.parse_args()

    for filepath in args.files:
        basename = os.path.basename(filepath)
        # 除外リストにある場合はスキップ
        if basename in IGNORE_LIST:
            print(f'Skipped ignored file: {basename}', file=sys.stderr)
            continue
        if not os.path.isfile(filepath):
            print(f'Error: file not found: {filepath}', file=sys.stderr)
            sys.exit(1)
        try:
            process_file(filepath)
        except Exception as e:
            print(f'Error processing {filepath}: {e}', file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
