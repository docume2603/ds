# サイトのフッター部分の Copyright を最終更新日表示に変える


## 履歴

(2024-08-13) 改定<br/>
(2024-07-01) 作成。（手抜き版）

## 方法

docusaurus.config.js の一部を以下のように書き換える。

なお、`last_update.text` は make_local_build.sh の末尾で次のように生成している。

```bash
date '+%Y-%m-%d %H:%M:%S' >last_update.text
```


## docusaurus.config.js の変更箇所

```js
import {themes as prismThemes} from 'prism-react-renderer';
import fs from 'fs';
import path from 'path';

const lastUpdatePath = path.resolve(__dirname, 'last_update.text');
let lastUpdateDate = '';

try {
    const data = fs.readFileSync(lastUpdatePath, 'utf8');
    // 日付部分を取得する（先頭10文字）
    lastUpdateDate = data.trim().slice(0, 10);
} catch (err) {
    console.error('Error reading last_update.text file:', err);
}

// 途中省略
// 途中省略
// 途中省略
// 途中省略


          copyright: `最新更新：${lastUpdateDate}, サイト管理者：横着者, Built with Docusaurus.`,
      },
      prism: {

```

(2024-08-13)
