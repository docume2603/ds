#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 2025-07-24 ChatGPT 4.2 で作成。

import sys
import shutil
import os
import re

USAGE = '''Usage:
  ./remove_autogen_index.py in.md

  - 指定ファイルのバックアップ in.md_bk を生成（上書き）
  - "## 目次" から "<!-- end of autogen index -->" までを
    "<!-- index here -->" に置換して保存（元ファイル上書き）

  ./remove_autogen_index.py -h
    このヘルプを表示
'''

def show_usage():
    print(USAGE.strip())

def main():
    # ヘルプ表示
    if len(sys.argv) == 2 and sys.argv[1] == '-h':
        show_usage()
        sys.exit(0)
    # 引数チェック
    if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
        print('Error: ファイルは1個だけ指定してください。\n', file=sys.stderr)
        show_usage()
        sys.exit(1)
    fname = sys.argv[1]
    if not os.path.isfile(fname):
        print(f'Error: ファイルが見つかりません: {fname}', file=sys.stderr)
        sys.exit(1)
    # バックアップ作成
    shutil.copy2(fname, fname + '_bk')

    # ファイル読み込み
    with open(fname, encoding='utf-8') as f:
        text = f.read()

    # 目次ブロックの正規表現
    # "## 目次"で始まり、<!-- end of autogen index -->を含む最短の範囲
    pattern = re.compile(
        r'^\s*## 目次\s*\n.*?^\s*<!-- end of autogen index -->\s*\n?', 
        re.DOTALL | re.MULTILINE
    )
    # 置換
    new_text, n = pattern.subn('<!-- index here -->\n', text, count=1)

    # 上書き
    with open(fname, 'w', encoding='utf-8', newline='') as f:
        f.write(new_text)

    if n == 0:
        print('警告: 目次ブロックが見つかりませんでした。', file=sys.stderr)

if __name__ == '__main__':
    main()
