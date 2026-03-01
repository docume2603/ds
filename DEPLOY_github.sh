#!/usr/bin/bash
## GitHub に deloy するためのスクリプト
#
# 2025-04-06 GitHub の 50MBファイルサイズ制限に強引対応
# 2024-07-11 環境変数設定を追加。shebang を冒頭に追加。
# 2024-07-25 作成
#
# GitHub 用の環境変数の設定
export GIT_USER=docume2603
export CURRENT_BRANCH=main
export USE_SSH=true
export GIT_USER_EMAIL=docume2603@gmail.com
export GIT_USER_NAME=docume2603

# 2025-04-06 変更分
# このスクリプトを実行する前に必ず、
# ./make_local_build.sh
# を実行すること。この make_local_build.sh で build し、
# その後に、50MB 以上の巨大ファイルの削除がなされる。
# 以下のスクリプトでは、build は省略した deploy がなされる筈。



# 2025-04-06 以下の処理は不要なので、コメントアウト
#
# 一旦、./build を削除
# if [ -d ./build ]; then
#     rm -rf build
#     if [ $? -ne 0 ]; then
#         echo "FAIL: rm -rf build"
#         exit 1
#     else
#         echo "PASS: rm -rf build"
#     fi
# fi
#
# # git add . を実行
# git add .
# if [ $? -ne 0 ]; then
#     echo "FAIL: git add ."
#     exit 1
# else
#     echo "PASS: git add ."
# fi
#
# # git commit を実行
# git commit -m "$commit_message"
# if [ $? -ne 0 ]; then
#   echo "FAIL: git commit"
#   exit 1
# else
#   echo "PASS: git commit"
# fi





# npm run deploy を実行

# 以下の --skip-buid オプションはまだテストしていない
#
#- `deploy --skip-bud` には --out_dir と wibsite の指定が必要かも？
#     - [v2] build -> deploy doesn't work · Issue #3452 · facebook/docusaurus  https://github.com/facebook/docusaurus/issues/3452

npm run deploy -- --skip-build
if [ $? -ne 0 ]; then
    echo "FAIL: npm run deploy -- --skip-build"
    exit 1
else
    echo "PASS: npm run deploy -- --dkip_build"
fi






# 古い方式
# npm run deploy
# if [ $? -ne 0 ]; then
#     echo "FAIL: npm run deploy"
#     exit 1
# else
#     echo "PASS: npm run deploy"
# fi

