#!/bin/bash
# -*- coding: utf-8 -*-
#
# Local PC の Apache で動作確認するためのスクリプト
#
# 2025-04-06
#    - GitHub の最大ファイルサイズ制限の対策を追加。
#    - git add . の順番をミスっていたので修正
# 2025-03-30 疑似リンク処理を削除。Docusaurus で作成するサイトの左バーの方式を全面的に変更して久しい。すでに疑似リンク処理は不要となった。
# 2024-08-20 追加。
# 2024-07-11 追加。疑似リンク処理を追加。
# 2024-07-06 追加。
# 2024-07-04 作成。

# Node.js のヒープ不足対策
# export NODE_OPTIONS="--max-old-space-size=12288"

# --- デフォルト値とフラグ ---
commit_message="fix or add article"
clear_cache=false

# --- ヘルプメッセージを表示する関数 ---
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Description:"
    echo "  Checks for broken links, commits changes, and builds the project."
    echo ""
    echo "Options:"
    echo "  -m <message>    Specify the git commit message (default: \"$commit_message\")."
    echo "  -c, --clear     Clear the cache (rm -rf node_modules/.cache) before building."
    echo "  -h              Display this help message and exit."
    exit 0
}

# --- コマンドラインオプションの解析 ---
# getopts が解釈できないロングオプションや、即時終了するオプションを先に処理する
for arg in "$@"; do
  case $arg in
    -h)
      show_help
      ;;
    --clear)
      clear_cache=true
      ;;
  esac
done

# getopts を使って、引数を取るオプションとショートオプションを解析する
while getopts "m:c" opt; do
  case $opt in
    m)
      commit_message=$OPTARG
      ;;
    c)
      clear_cache=true
      ;;
    \?) # 不正なオプション
      echo "Invalid option: -$OPTARG" >&2
      show_help
      exit 1
      ;;
  esac
done

# 動作の厳密化
set -euo pipefail

# 最初に ./blog/*.md_bk を削除
# find ./blog -type f -name "*.md_bk" | xargs rm
find ./blog -type f -name "*.md_bk" -exec rm {} \;


# ① 対象ディレクトリを固定
TARGET_DIR="./static/img"

# ② 存在チェック（オプション）
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: directory '$TARGET_DIR' not found" >&2
  exit 1
fi

# ③ チェックフラグ
failed=false

# ④ ディレクトリ直下の全ファイルループ（サブディレクトリは含まない）
for filepath in "$TARGET_DIR"/*; do
  # ファイルでなければスキップ
  [[ -f "$filepath" ]] || continue

  filename=${filepath##*/}

  # gh_ で始まらない場合は出力＆フラグ立て
  if [[ "$filename" != gh_* ]]; then
    echo "$filepath"
    failed=true
  fi
done

# ⑤ 異常ファイルがあったら exit 1
if [[ "$failed" == true ]]; then
  echo "FAIL: filename pre-fix check (./static/img/)"
  exit 1
fi

# ⑥ 全件 OK の場合は以下の処理を継続。
echo "PASS: filename pre-fix check (./static/img/)"



# 内部リンク先の存在チェック
python md_link_check.py .
if [ $? -ne 0 ]; then
  echo "FAIL: python md_link_check.py"
  exit 1
else
  echo "PASS: python md_link_check.py"
fi

# git add . を実行
git add .
if [ $? -ne 0 ]; then
  echo "FAIL: git add ."
  exit 1
else
  echo "PASS: git add ."
fi

# ソースファイルに変更があるかを確認
if git diff-index --quiet HEAD --; then
  echo "No changes to commit."
  exit 0
fi

# ディレクトリが存在する場合、削除する
if [ -d ./build ]; then
  rm -rf build
  if [ $? -ne 0 ]; then
    echo "FAIL: rm -rf build"
    exit 1
  else
    echo "PASS: rm -rf build"
  fi
fi

# git commit を実行
git commit -m "$commit_message"
if [ $? -ne 0 ]; then
  echo "FAIL: git commit"
  exit 1
else
  echo "PASS: git commit"
fi

# --- オプションに応じてキャッシュを削除 ---
if [ "$clear_cache" = true ]; then
  echo "-> Found -c or --clear option. Clearing cache..."
  if [ -d "node_modules/.cache" ]; then
    rm -rf node_modules/.cache
    if [ $? -ne 0 ]; then
      echo "FAIL: rm -rf node_modules/.cache"
      exit 1
    else
      echo "PASS: rm -rf node_modules/.cache"
    fi
  else
    echo "INFO: 'node_modules/.cache' directory not found. Skipping cache clear."
  fi
fi

# npm run build を実行
npm run build
if [ $? -ne 0 ]; then
  echo "FAIL: npm run build"
  exit 1
else
  echo "PASS: npm run build"
fi

# GitHub 対応のため、50MB を超えるサイズのファイルを削除。なぜ Docusaurus が 50MB 以上のサイズのファイルを生成するのか、理由も使用目的も不明だが、local Apache では削除しても問題ないようなので GitHub でも大丈夫と予想。
python delete_size_over_files.py
if [ $? -ne 0 ]; then
  echo "FAIL: delete_size_over_files.py"
  exit 1
else
  echo "PASS: delete_size_over_files.py"
fi


# date > last_date.text
date '+%Y-%m-%d %H:%M:%S' >last_update.text
