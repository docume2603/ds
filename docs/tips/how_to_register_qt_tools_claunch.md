---
tags: [tech]
---

# PyQt で作成した GUI ツールを CLaunch で起動する方法


## 前置き

Docusaurus でサイトの記事を効率的に作成、管理するために様々なツールを使っている。build や deploy は 端末操作の方が手早いが、画像埋め込み、文字起こし、記事のデータベース化、検索などは GUI ツールの方が扱いやすい。

こういった Windows 環境用の自作 GUI ツールが幾つもあるため、それらを CLaunch から起動する方法を記録しておく。

このような些細かつ非系統的な雑ネタはすぐに忘れるので記録しておく。

## 何が問題か？

CLaunch から起動するにしても、通常の Windows のバッチファイルから GUI ツールを呼び出す方式では、Windows のコマンド・プロンプト画面が表示され、この画面が邪魔でウザい。

ウザいが、コマンド・プロンプトは機能が貧弱なので、消すには泥臭い小細工が必要になる（例：タスク・スケジューラとか VB とか引っ張り出してゴニョゴニョ）。

## 対処

そこで、コマンド・プロンプトを捨てて、Git-bash 端末から起動する方法をとる。Git-bash 端末には起動パラメータ(*1)として `--hide` や `no-needs-console` が用意されているので小細工は不要となる。

以下のように GUI ツールを登録する。以下の例では `run_qt_img_path_conv.sh` (*2)という bash スクリプトを登録している。この bash スクリプトから PyQt5 で作成した GUI ツールの `qt_img_path_conv.py` (*3)を起動することになる。

bash スクリプトで miniconda による仮想環境の中に入り、その仮想環境で PyQt スクリプトを実行させている。

## CLaunch での登録手順

1. CLaunch の空いているセルに 登録したい bash スクリプトを drag & drop する。
2. そのセルを右クリックして「プロパティ」を選択し、以下の画面のように必要箇所を設定する。

<a href="/ds/img/gh_20240724_ppt_set.jpg" target="_blank"><img  alt="gh_20240724_ppt_set.jpg" border="0" src="/ds/img/gh_20240724_ppt_set.jpg" width="90%"/></a>

<a href="/ds/img/gh_20240724_ppt_set2.jpg" target="_blank"><img  alt="gh_20240724_ppt_set2.jpg" border="0" src="/ds/img/gh_20240724_ppt_set2.jpg" width="90%"/></a>


## (*1)

'Git-bash' の起動パラメータの一覧は Git-bash 端末から `git help git-bash` と入力することで「ブラウザ」に表示される。

## (*2)

```bash title="run_qt_img_path_conv.sh"
#!/usr/bin/bash
source activate pyqt
cd /c/my_prog/iso_mp4_pyqt
python  qt_img_path_conv.py
```

## (*3)

```python title="qt_img_path_conv.py"
# -*- coding: utf-8 -*-
"""
機能：
Explore から JPEG 画像ファイルを drag & drop すると
Docusaurus 向けの書式に変換する。


履歴：
2024-07-11 作成

"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QClipboard
from PyQt5.QtCore import Qt, QMimeData
import os

class DragDropWindow(QWidget):
    def __init__(self):
        super().__init__()

        css = """
        background-color: #cccccc;
        color: #000000;
        font-family: Times;
        font-weight: bold;
        font-size: 24px;
        """
        self.setStyleSheet(css)

        self.setWindowTitle("JPEG Drag & Drop Tool")
        self.setGeometry(300, 300, 600, 400)
        self.textEdit = QTextEdit()
        self.textEdit.setAcceptDrops(False)
        self.textEdit.setReadOnly(True)

        self.convertButton = QPushButton("画像リンク化")
        self.convertButton.clicked.connect(self.convertToLinks)

        self.copyButton = QPushButton("クリップボードへコピー")
        self.copyButton.clicked.connect(self.copyToClipboard)

        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(self.convertButton)
        layout.addWidget(self.copyButton)
        self.setLayout(layout)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            base_names = []
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith(".jpeg") or file_path.lower().endswith(".jpg"):
                        base_name = os.path.basename(file_path)
                        base_names.append(base_name)
            base_names.sort()  # ソート処理
            self.textEdit.clear()
            for base_name in base_names:
                self.textEdit.append(base_name)
            event.acceptProposedAction()

    def convertToLinks(self):
        text = self.textEdit.toPlainText()
        lines = text.split('\n')
        converted_lines = []
        for line in lines:
            if line.strip():
                converted_lines.append(f'<a href="/ds/img/{line}" target="_blank">'
                                       f'<img alt="{line}" border="0" src="/ds/img/{line}" width="90%"/></a>\n')
        self.textEdit.setPlainText('\n'.join(converted_lines))

    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.textEdit.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropWindow()
    window.show()
    sys.exit(app.exec_())
```

(2024-07-24)
