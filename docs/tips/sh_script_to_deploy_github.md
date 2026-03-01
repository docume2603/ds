# GitHub に deploy するための bash script


:::info[注意]

以下は万人向けの解説ではなく、私的な忘備録。
環境は Windows11 + miniconda

GitHub で Docusaurus 専用の repository を作成し、Pages の設定を既に済ませているものと想定している。

:::

## deploy の手順

Git-bash 端末から以下を実行する。

1. 最初に専用の miniconda 環境に入ってから、作業 directory に cd する。
```bash title="bash"
conda activate docusaurus
cd /c/my_prog/docusaurus/github_page
```
2. 記事の追加や編集（blog や docs/UFO などの該当する directory で作業）
1. ディレクトリを移動。
`cd /c/my_prog/docusaurus/github_page`
1. local PC の Apache で確認。
`./make_local_build.sh`
1. local PC の Git-bash で以下を実行。
`./DEPLOY_github.sh`

## deploy 用 bash script

```bash title="DEPLOY_github.sh"
#!/usr/bin/bash
## GitHub に deloy するためのスクリプト
#
# 2025-04-06 GitHub の 50MBファイルサイズ制限に強引対応
# 2024-07-11 環境変数設定を追加。shebang を冒頭に追加。
# 2024-07-25 作成
#
# GitHub 用の環境変数の設定
export GIT_USER=XXXXX
export CURRENT_BRANCH=main
export USE_SSH=false


# 2025-04-06 変更分
# このスクリプトを実行する前に必ず、
# ./make_local_build.sh
# を実行すること。この make_local_build.sh で build し、
# その後に、50MB 以上の巨大ファイルの削除がなされる。
# 以下のスクリプトでは、build は省略した deploy がなされる筈。



# npm run deploy を実行
npm run deploy -- --skip-build
if [ $? -ne 0 ]; then
    echo "FAIL: npm run deploy -- --skip-build"
    exit 1
else
    echo "PASS: npm run deploy -- --dkip_build"
fi

```



## 履歴

(2025-05-14) 改定

(2024-07-13) 作成

