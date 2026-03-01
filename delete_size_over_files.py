#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
履歴：
2025-04-06 : ChatGPT o3-mini-ihgh で作成。

参考：
仕様文章（直後の段落）の整理も以下のようにして AI に依頼した。

d) 上述の「スクリプトの仕様」はこの場でざっと思いつきを書いただけで、仕様書としては整理されていません。そこでそれを若干、整理した文章にした上で、以下のようにスクリプトの冒頭部分に埋め込んで。後で、これが何のスクリプトか、直ぐに理解できるようにする目的です。

"""


r"""
delete_size_over_files.py

概要:
　このスクリプトは、ハードコードされた複数のディレクトリ（target_dir1, target_dir2 等）内を再帰的に走査し、
　指定されたサイズ（max_file_size で指定、例："50MB"）以上のファイルをリストアップして表示します。
　該当ファイルが存在する場合、ユーザに削除確認（y/n）を求め、'y' または 'Y' の場合にファイルを削除します。

仕様:
1. 内部変数として target_dir1 と target_dir2 をユーザが直接指定します（例: "./build/assets/js"、"./build/en/assets/js"）。
   指定したディレクトリが存在しなければ、エラーメッセージを表示して終了（終了コード 1）。

2. max_file_size 変数でファイルサイズの閾値を指定します。必ず "MB" 単位で指定する必要があり、単位がなければエラー終了（終了コード 1）。
   例: max_file_size = "50MB"

3. 各 target_dir に対して、そのディレクトリとサブディレクトリ内のファイルを走査し、
   max_file_size 以上のサイズのファイルを全てリストアップして、ファイルパスとファイルサイズ（バイト単位）を表示します。
   該当するファイルが一件も存在しなければ、その旨を表示して正常終了（終了コード 0）。

4. 【削除確認部分】
   ユーザに対して、リストアップしたファイルを削除してよいかどうか y/n で確認します。
   'y' または 'Y' 以外の入力の場合は、処理を中断して終了（終了コード 1）。
   ※ この部分は後でコメントアウトしやすいよう、「ここから」「ここまで」の注記を付けています。

5. ユーザの確認後、対象ファイルを全て削除します。

6. スクリプトはコマンドライン引数として -h オプションを受け付け、ヘルプメッセージを表示します。
   その他の引数は受け付けません。

7. エラー終了時は終了コード 1、正常終了時は 0 を返します。

改善案:
　・削除前の確認プロセスをログ出力やバックアップ機能と連携させることで、誤削除防止やトラブルシューティングを容易にできます。
　・現状はパラメータをハードコードしていますが、将来的には設定ファイルから読み込む方式にすることで、柔軟性が向上します。
"""

import os
import sys

# ヘルプオプションの処理
if len(sys.argv) > 1 and sys.argv[1] == "-h":
    print("Usage: delete_size_over_files.py")
    print("このスクリプトは、指定されたディレクトリ内のファイルのうち、")
    print("指定サイズ（MB単位）以上のファイルをリストアップし、ユーザ確認後に削除します。")
    sys.exit(0)

# ユーザが直書きするパラメータ
target_dir1 = "./build/assets/js"
target_dir2 = "./build/en/assets/js"
# 将来 target_dir3, target_dir4 などが追加される可能性を考慮してリストにまとめる
target_dirs = [target_dir1, target_dir2]

max_file_size = "50MB"  # 例: "50MB" と指定

# max_file_size の形式チェック（"MB" 単位が必須）
if not max_file_size.upper().endswith("MB"):
    print("エラー: max_file_size は必ず 'MB' 単位で指定してください。")
    sys.exit(1)

try:
    # 数値部分を抽出し、バイト単位に変換（1MB = 1024*1024 バイト）
    size_value = float(max_file_size[:-2].strip())
except ValueError:
    print("エラー: max_file_size の数値部分が正しくありません。")
    sys.exit(1)

threshold = size_value * 1024 * 1024  # 比較用の閾値（バイト単位）

# 指定された各ディレクトリの存在確認
for d in target_dirs:
    if not os.path.isdir(d):
        print(f"エラー: 指定されたディレクトリ {d} は存在しません。")
        sys.exit(1)

# 対象ファイルを格納するリスト
files_to_delete = []

# 各ディレクトリ内（サブディレクトリ含む）のファイルを走査し、指定サイズ以上のファイルをリストアップ
for d in target_dirs:
    for root, dirs, files in os.walk(d):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                filesize = os.path.getsize(filepath)
            except OSError as e:
                print(f"エラー: {filepath} のサイズ取得に失敗しました。{e}")
                continue
            if filesize >= threshold:
                # ファイルパスとサイズ（バイト単位）を表示
                print(f"{filepath} - {filesize} バイト")
                files_to_delete.append(filepath)

# 指定サイズ以上のファイルが一件もなかった場合
if not files_to_delete:
    print("指定されたサイズ以上のファイルは存在しません。")
    sys.exit(0)

"""
# ここから: ユーザ確認部分（削除確認）
user_input = input("上記のファイルを削除してもよろしいですか？ (y/n): ")
if user_input.lower() != 'y':
    print("処理を中断します。")
    sys.exit(1)
# ここまで: ユーザ確認部分
"""

# 対象ファイルの削除処理
for filepath in files_to_delete:
    try:
        os.remove(filepath)
        print(f"削除しました: {filepath}")
    except Exception as e:
        print(f"エラー: {filepath} の削除に失敗しました。 {e}")

sys.exit(0)
