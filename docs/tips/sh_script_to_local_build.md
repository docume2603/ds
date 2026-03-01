# local build 用 bash script

:::info[注意]

以下は万人向けの解説ではなく、私的な忘備録。
環境は Windows11 + miniconda

GitHub で Docusaurus 専用の repository を作成し、Pages の設定を既に済ませているものと想定している。

:::


## local build の手順

Git-bash 端末から以下を実行する。

1. 最初に専用の miniconda 環境に入ってから、作業 directory に cd する。
```bash title="bash"
conda activate docusaurus
cd /c/my_prog/docusaurus/github_page
```
2. 記事の追加や編集（blog や docs/UFO などの該当する directory で作業）
1. ディレクトリを移動。
`cd /c/my_prog/docusaurus/github_page`
1. build を実行。
`./make_local_build.sh`
1. local PC の Apache でサイトを確認。

## local build 用 bash script

```bash title="make_local_build.sh"
#!/bin/bash
# -*- coding: utf-8 -*-
#
# Local PC の Apache で動作確認するためのスクリプト
#
# 2025-04-06
#    - GitHub の最大ファイルサイズ制限の対策を追加。
#    - git add . の順番をミスっていたので修正
# 2025-03-30 疑似リンク処理を削除。Dodusaurus で作成するサイトの左バーの方式を全面的に変更して久しい。すでに疑似リンク処理は不要となった。
# 2024-08-20 追加。
# 2024-07-11 追加。疑似リンク処理を追加。
# 2024-07-06 追加。
# 2024-07-04 作成。AI 支援。

# デフォルトのコミットメッセージ
commit_message="fix or add article"

# 疑似リンク処理はもう不要となった。2025-03-23
#
# 疑似リンクの処理
# python solv_pseudo_symlink.py
# if [ $? -ne 0 ]; then
#   echo "FAIL: python solv_pseudo_symlink.py"
#   exit 1
# else
#   echo "PASS: python solv_pseudo_symlink.py"
# fi


# このブロックは 2025-04-25 に追加。./static/img の内部をチェックし、
# "gh_" で始まらないファイルがあれば、処理を中断。
#
# 動作の厳密化、
set -euo pipefail

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


# コマンドラインオプションの解析
while getopts "m:" opt; do
  case $opt in
    m)
      commit_message=$OPTARG
      ;;
    *)
      echo "Usage: $0 [-m commit_message]"
      exit 1
      ;;
  esac
done

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
```

## 履歴

(2025-05-14) 改定

(2024-07-13) 作成
