# build の手順


:::info[注意]

以下は万人向けの解説ではなく、私的な忘備録。
環境は Windows11 + miniconda

:::



## 前置き

以下は手で逐次的に作業する場合の手順。実際は 
[local build 用 bash script](sh_script_to_local_build.md)
のスクリプトを実行するのが手早い。

## 手順

Git-bash 端末から以下を実行


1. 最初に専用の miniconda 環境に入ってから、作業 directory に cd する。
```bash
conda activate docusaurus
cd /c/my_prog/docusaurus_test/test-website
```
2. ドキュメントを編集。

3. ディレクトリを移動。
`cd /c/my_prog/docusaurus_test/test-website`

4. ディレクトリ `build` を消してから、buid コマンドを実行。
```bash
rm -rf build; npm run build
```


:::warning[重要]

あらかじめ `rm -rf build` をしておかないと、原因不明のエラーが多発する。

:::


:::note[予定]

いずれ Docusaurus によるサイト構築は WSL2 上の Docker 環境に移行したい。

Git-bash だとやはりなにかと不自由だし、PowerShell ではに牛刀割鶏になる。（牛刀割鶏＝チェーンソーで鉛筆を削る、大木＝Active Directory、 一般の Windows ユーザは Active Directory なんてものを管理する苦行とは無縁）

:::


## 履歴

- (2024-07-02) 作成
- (2024-07-13) 追加
