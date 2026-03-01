# GitHub に deploy する手順


:::info[注意]

以下は万人向けの解説ではなく、私的な忘備録。
環境は Windows11 + miniconda

GitHub で Docusaurus 専用の repository を作成し、Pages の設定を既に済ませているものと想定している。

:::

## 前置き

以下は手で逐次的に作業する場合の手順。実際は 
[GitHub に deploy するための bash script](sh_script_to_deploy_github.md)
のスクリプトを実行するのが手早い。

## 環境変数の設定

予め、local PC の Git-bash に以下の環境変数を設定しておく。後述の `.git/config` で設定しても良い。

1. export GIT_USER=＜USER_NAME＞
1. exprot CURRENT_BRANCH=main
1. export USE_SSH=false


## Git の初期設定

`.git/config` に以下のように設定する。
```bash title=".git/config"
[core]
        repositoryformatversion = 0
        filemode = false
        bare = false
        ignorecase = true
[user]
  name = ＜USER_NAME＞
  email = ＜USER_EMAIL_ADDRESS＞
[remote "origin"]
        url = https://github.com/＜USER_NAME＞/ds.git
[branch "main"]
        remote = origin
        merge = refs/heads/main
```

あるいは、個別コマンドで以下のように設定。

```bash title="bash"
git branch -M main
git remote add origin https://github.com/＜USER_NAME＞/＜REPOSITORY_NANME＞.git
git push -u origin main
```

# deploy の手順

Git-bash 端末から以下を実行する。

1. 最初に専用の miniconda 環境に入ってから、作業 directory に cd する。
```bash title="bash"
conda activate docusaurus
cd /c/my_prog/docusaurus/github_page
```
1. ドキュメントを編集。
1. ディレクトリを移動。
`cd /c/my_prog/docusaurus/github_page`
1. local PC の Git-bash で以下を実行。
    1. rm -rf buld/
    1. git add .
    1. git commit -m "..."
    1. npm run deploy

:::warning[重要]

あらかじめ `rm -rf build` をしておかないと、`npm run deploy` で原因不明のエラーが多発する。

:::

## 履歴

- (2024-07-13) 追加
- (2024-07-02) 作成

