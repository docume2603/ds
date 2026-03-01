#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pathlib
import shutil
import sys
import os
import re
from typing import List, Tuple

r"""
履歴
2025-08-12 編集中のファイルがあれば中止
2025-08-09 '_' で始まるファイルも無視するように変更。
2025-08 作成

"""

# --- 設定項目 ---
# 同期したいディレクトリのペアをタプルのリストとして定義します。
# (deploy_path, local_path) の順で指定してください。
#
# pathlib.Path を使うことで、Windows と MINGW64/Linux の
# パス区切り文字の違いを吸収できます。
#
# 例:
# PATH_PAIRS = [
#     (pathlib.Path("C:/Users/YourUser/Project/deploy/blog"), pathlib.Path("C:/Users/YourUser/Project/local/blog")),
#     (pathlib.Path("C:/Users/YourUser/Project/deploy/assets"), pathlib.Path("C:/Users/YourUser/Project/local/assets")),
#     (pathlib.Path(""), pathlib.Path("")), # この行のように空のパスを指定するとスキップされます
# ]

PATH_PAIRS: List[Tuple[pathlib.Path, pathlib.Path]] = [
    (pathlib.Path(r"c:/my_prog/docusaurus/github_page/blog"), pathlib.Path("c:/my_prog/docusaurus/fast_github_page/blog")),
    (pathlib.Path(r"c:/my_prog/docusaurus/github_page/static/img"), pathlib.Path(r"c:/my_prog/docusaurus/fast_github_page/static/img")),
    (pathlib.Path(""), pathlib.Path("")), # スキップさせたい場合は空のままにする
]
# --- 設定はここまで ---


def create_copy_plan(
    deploy_path: pathlib.Path, local_path: pathlib.Path
) -> List[Tuple[pathlib.Path, pathlib.Path]]:
    """
    指定された deploy_path と local_path を比較し、
    コピーが必要なファイルのリスト（実行計画）を作成する。
    """
    copy_plan = []

    # 有効な base file の文字
    valid_filename_pattern = re.compile(r'^[0-9a-zA-Z_\-@]+$')

    # local_path 内のすべてのファイルを再帰的に探索
    for local_file in local_path.rglob("*"):
        if not local_file.is_file():
            continue
        if local_file.suffix.lower() in ['.md_bk', '.mdx_bk']:
            continue
        # 2025-08-12 追加。編集中のファイルを検出
        base_filename = os.path.basename(local_file)
        non_ext_part = os.path.splitext(base_filename)[0]
        if not valid_filename_pattern.match(non_ext_part):
            print(f"{base_filename=}, {non_ext_part=}")
            print(f"Error!: Illegal filename:{local_file}")
            sys.exit(1)
        # ファイル名がアンダースコアで始まる場合は無視
        if local_file.name.startswith('_'):
            continue
        # deploy_path 側に対応するファイルのパスを計算
        relative_path = local_file.relative_to(local_path)
        deploy_file = deploy_path / relative_path

        # 1. deploy側にファイルが存在しない場合 -> localからdeployへコピー
        if not deploy_file.exists():
            copy_plan.append((local_file, deploy_file))
            continue

        # 2. 両方にファイルが存在する場合、変更日時を比較
        local_mtime = local_file.stat().st_mtime
        deploy_mtime = deploy_file.stat().st_mtime

        if local_mtime > deploy_mtime:
            # local の方が新しい -> localからdeployへコピー
            copy_plan.append((local_file, deploy_file))
        elif deploy_mtime > local_mtime:
            # deploy の方が新しい -> deployからlocalへコピー
            copy_plan.append((deploy_file, local_file))

    return copy_plan


def execute_copy(source: pathlib.Path, destination: pathlib.Path):
    """
    ファイルを実際にコピーする。コピー先のディレクトリがなければ作成する。
    """
    try:
        # コピー先の親ディレクトリが存在しない場合は作成
        destination.parent.mkdir(parents=True, exist_ok=True)
        # メタデータ（変更日時など）を維持してコピー
        shutil.copy2(source, destination)
        print(f"COPIED: {source} -> {destination}")
    except Exception as e:
        print(f"ERROR: コピー中にエラーが発生しました。({source} -> {destination})", file=sys.stderr)
        print(f"       {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    メイン処理
    """
    parser = argparse.ArgumentParser(
        description="2つのディレクトリ間で、local_pathに存在するファイルを基準にファイルの同期を行います。"
    )
    parser.add_argument(
        "-v", "--verify",
        action="store_true",
        help="コピーを実行する前に、実行内容を表示してユーザーに確認を求めます。"
    )
    args = parser.parse_args()

    # すべてのペアから生成されたコピー計画を格納するリスト
    full_copy_plan = []

    for deploy_path, local_path in PATH_PAIRS:
        # パスが空の場合はスキップ
        if not str(deploy_path) or not str(local_path):
            continue

        # 指定されたパスが存在するかチェック
        if not deploy_path.is_dir() or not local_path.is_dir():
            print(f"ERROR: 指定されたディレクトリが存在しません。", file=sys.stderr)
            print(f"       - deploy: {deploy_path}", file=sys.stderr)
            print(f"       - local:  {local_path}", file=sys.stderr)
            sys.exit(1)

        # このペアのコピー計画を作成し、全体の計画に追加
        pair_copy_plan = create_copy_plan(deploy_path, local_path)
        full_copy_plan.extend(pair_copy_plan)

    # 実行すべきコピーがない場合
    if not full_copy_plan:
        print("同期するファイルはありません。")
        sys.exit(0)

    print(f"【同期計画】 {len(full_copy_plan)} 件のファイルコピーが見つかりました。")
    for source, destination in full_copy_plan:
        print(f"  COPY: {source}\n    ->  {destination}")

    # 確認オプションが有効な場合
    if args.verify:
        try:
            choice = input("\n以上のコピーを実行しますか？ (Y/n): ")
            if choice.lower() != 'y':
                print("キャンセルされました。")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\nキャンセルされました。")
            sys.exit(0)

    # コピー処理の実行
    print("\nコピー処理を開始します...")
    for source, destination in full_copy_plan:
        execute_copy(source, destination)

    print("\nすべての同期処理が正常に完了しました。")
    sys.exit(0)


if __name__ == "__main__":
    main()
