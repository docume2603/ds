#!/usr/bin/env python
# -*- coding: utf-8 -*-


r"""


用途：

ouchaku アカウントで作成した blog 記事のリンク URL を 書き換えて
ume2509 アカウントからリンクが張れるようにするツール。

たとえば、/c/my_prog/docusaurus/github_page/docs/ufo/index_ufo.md

を

/c/my_prog/docusaurus/ume2509/docs/ufo/index_ufo.md

にコピーしたとする。このコピーした index_ufo.md の


1. [1964-05-23, UK : 有名な「子供の背後にスペースマンが写り込んだ写真」 → この謎を解く（書式変換）](/ds/blog/2024/10/05/uk_girl_spaceman) <br/><img  alt="gh_20131220_jim_templeton.jpg" border="0" src="/ds/img/gh_20131220_jim_templeton.jpg" height="150" align="top"/> <img  alt="gh_20220816_girl_enlarge.jpg" border="0" src="/ds/img/gh_20220816_girl_enlarge.jpg" height="150" align="top"/>

の箇所は

1. [1964-05-23, UK : 有名な「子供の背後にスペースマンが写り込んだ写真」 → この謎を解く（書式変換）](https://ouchaku.github.io/ds/blog/2024/10/05/uk_girl_spaceman) <br/><img  alt="gh_20131220_jim_templeton.jpg" border="0" src="https://ouchaku.github.io/ds/img/gh_20131220_jim_templeton.jpg" height="150" align="top"/> <img  alt="gh_20220816_girl_enlarge.jpg" border="0" src="https://ouchaku.github.io/ds/img/gh_20220816_girl_enlarge.jpg" height="150" align="top"/>

に書き換えないと、サイトが異なるのでアクセスできない。この書き換えを行うのが本ツール。


履歴：
 2025-09-07 <a href="https://ouchaku.github.io/ds/img/gh_20240629_boy_10150.jpg" にも対応。

 2025-09-06 Gemini Flush 2.5 が作成。

"""


import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

# カスタムQTextEditクラス
# ドラッグ＆ドロップ機能を処理するために、QTextEditを継承します。
class DragDropTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    # ドラッグされたアイテムがこのウィジェットに受け入れられるか判断
    def dragEnterEvent(self, event: QDragEnterEvent):
        # ファイルのURLがあるか、かつファイル数が1つか確認
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            url = event.mimeData().urls()[0]
            # .md 拡張子を持つファイルか確認
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.md'):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    # ドロップされたアイテムを処理
    def dropEvent(self, event: QDropEvent):
        url = event.mimeData().urls()[0]
        file_path = url.toLocalFile()

        try:
            # ファイルの内容を読み込んでQTextEditに表示
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ファイルの読み込み中にエラーが発生しました。\n{e}")

        event.acceptProposedAction()

# メインウィンドウクラス
class MarkdownConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("外部サイトからの引用目的: ouchaku blog の内部リンク変換")
        self.setGeometry(100, 100, 800, 600)

        self.resize(800, 800)

        css = """
            background-color: #cccccc;
            color: #000000;
            font-family: Times;
            font-weight: bold;
            font-size: 24px;
            """
        self.setStyleSheet(css)

        # ウィジェットの作成
        self.text_edit = DragDropTextEdit(self)

        self.btn_conv = QPushButton("リンク変換")
        self.btn_copy_clip_board = QPushButton("コピー")

        # レイアウトの作成
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.text_edit)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_conv)
        button_layout.addWidget(self.btn_copy_clip_board)

        main_layout.addLayout(button_layout)

        self.setCentralWidget(main_widget)

        # シグナルとスロットの接続
        self.btn_conv.clicked.connect(self.convert_text)
        self.btn_copy_clip_board.clicked.connect(self.copy_to_clipboard)

        # テキストが変更されたときにボタンのラベルをリセット
        self.text_edit.textChanged.connect(self.reset_copy_button)

    # テキスト変換メソッド
    def convert_text(self):
        text = self.text_edit.toPlainText()

        # 正規表現による置き換え
        # 例1の変換
        # [テキスト](/ds/blog/...) -> [テキスト](https://ouchaku.github.io/ds/blog/...)
        text = re.sub(r'(\]\()/ds/blog/', r'\1https://ouchaku.github.io/ds/blog/', text)

        # 例2の変換
        # src="/ds/img/... -> src="https://ouchaku.github.io/ds/img/...
        text = re.sub(r'src="(/ds/img/)', r'src="https://ouchaku.github.io\1', text)

        # 例3の変換
        # <a href="/ds/img/gh_20240629_boy_10150.jpg" -> <a href="https://ouchaku.github.io/ds/img/gh_20240629_boy_10150.jpg"
        text = re.sub('<a +?href=\"/ds/img/', r'<a href="https://ouchaku.github.io/ds/img/', text)

        self.text_edit.setPlainText(text)
        self.btn_copy_clip_board.setText("コピー")

    # クリップボードへコピーするメソッド
    def copy_to_clipboard(self):
        text = self.text_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        self.btn_copy_clip_board.setText("コピー済")

    # コピーボタンのラベルをリセットするメソッド
    def reset_copy_button(self):
        self.btn_copy_clip_board.setText("コピー")

# アプリケーションの実行
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MarkdownConverter()
    window.show()
    sys.exit(app.exec_())
