#!/bin/bash
# -*- coding: utf-8 -*-

# 2024-07-27 追加
# 2024-07-26 作成
# ===========================================
#
#  Description:
#    引数で指定されたファイル、または指定された拡張子のファイルを検索して、
#    Pythonスクリプトを実行します。
#
#  Usage:
#    ./test1.sh [-h] [file1] [file2] ...
#    ./test1.sh --ext <extension>
#    ./test1.sh -e <extension>
#
# ============================================


# 動作の厳密化
set -euo pipefail

# --- ヘルプメッセージを表示する関数 ---
show_help() {
  echo "Usage: $(basename "$0") <command>"
  echo ""
  echo "Commands:"
  echo "  [file1] [file2] ...    Process specified files."
  echo "  --ext <ext>            Process all *.<ext> files in the current directory."
  echo "  -e <ext>               Alias for --ext."
  echo "  -h                     Show this help message and exit."
}

# --- 1つのファイルを処理する共通関数 ---
# この関数に処理をまとめることで、コードの重複を避けます。
process_file() {
  # 関数の第一引数をローカル変数 file に格納
  local file="$1"

  echo "--- Processing: $file ---"

  # Pythonスクリプトを実行し、失敗したらスクリプト全体をエラー終了させる
  # markdown 内部の自己サイト参照 URL リンクを書き換える。
  if ! python replace_url.py "$file"; then
    # Pythonスクリプトの実行が失敗した場合
    echo "ERROR: Python script(replace_url.py) failed for '$file'." >&2
    exit 1 # スクリプトをエラーコード1で即時終了
  fi
  echo "PASS: Python script(replace_url.py) $file ---"
  echo ""

  # markdown の **『強調部分』** の適正対処
  if ! python md_2astr_wrapper.py "$file"; then
    # Pythonスクリプトの実行が失敗した場合
    echo "ERROR: Python script(md_2astr_wrapper.py) failed for '$file'." >&2
    exit 1 # スクリプトをエラーコード1で即時終了
  fi
  echo "PASS: Python script(md_2astr_wrapper.py) $file ---"
  echo ""

  # 既に 目次が自動生成されていたら、それを削除
  if ! python remove_autogened_index.py "$file"; then
    # Pythonスクリプトの実行が失敗した場合
    echo "ERROR: Python script(remove_autogened_index.py) failed for '$file'." >&2
    exit 1 # スクリプトをエラーコード1で即時終了
  fi
  echo "PASS: Python script(remove_autogened_index.py) $file ---"
  echo ""

  # 目次を自動生成
  if ! python gen_index_md.py "$file"; then
    # Pythonスクリプトの実行が失敗した場合
    echo "ERROR: Python script(gen_index_md.py) failed for '$file'." >&2
    exit 1 # スクリプトをエラーコード1で即時終了
  fi
  echo "PASS: Python script(gen_index_md.py) $file ---"
  echo ""
}

#
# --- メイン処理 ---
#

# ヘルプオプションまたは引数なしの場合はヘルプを表示
if [[ "$1" == "-h" ]] || [[ $# -eq 0 ]]; then
  show_help
  exit 0
fi

# --ext または -e オプションが指定された場合の処理
if [[ "$1" == "--ext" ]] || [[ "$1" == "-e" ]]; then

  # 拡張子が指定されているかチェック ($2が存在しない、または空文字列)
  if [[ -z "$2" ]]; then
    echo "ERROR: An extension must be specified after the '$1' option." >&2
    show_help
    exit 1
  fi

  extension="$2"
  echo ">>> Searching for *.$extension files in the current directory..."
  echo ""

  # ファイルが見つかったかどうかのフラグ
  found_files=0

  # findコマンドで安全にファイルを検索し、whileループで1つずつ処理
  # -print0 と read -d '' の組み合わせで、スペース等を含むファイル名にも完全対応
  while IFS= read -r -d '' file; do
    process_file "$file"
    found_files=1
  done < <(find . -maxdepth 1 -type f -name "*.$extension" -print0)

  if [[ $found_files -eq 0 ]]; then
    echo "No '*.$extension' files found."
  fi

# オプションが指定されなかった場合（従来の処理）
else
  # スクリプト全体でエラーが発生したかを追跡するフラグ
  has_error=0

  # 引数で渡されたファイルを1つずつ処理
  for file in "$@"; do
    if [ -f "$file" ]; then
      process_file "$file"
    else
      echo "ERROR: File not found: '$file'" >&2
      has_error=1
    fi
  done

  # 1つでもファイル未検出エラーがあったら、最後にエラーで終了
  if [ $has_error -ne 0 ]; then
      echo ""
      echo "Execution finished with file-not-found errors." >&2
      exit 1
  fi
fi

echo "All tasks completed successfully."
exit 0
