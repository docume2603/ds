#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
ZWNJ Wrapper GUI

Windows11 + PyQt5 で Markdown ファイルをドラッグ＆ドロップし、
ゼロ幅非接合子(U+200C)による ** マーカーのラップとバックアップを実行します。
エラー時は一覧に「エラー: ファイル名」、正常時は「正常終了: ファイル名」と表示。
再変換時はエラー表示されたファイルのみ処理します。

依存: Python3, PyQt5, 標準ライブラリ
"""
import sys
import os
import shutil
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QMessageBox
)

# === 変換除外リスト（basename+拡張子） ===
IGNORE_LIST = ['2025-07-14-hack_ai_generated_md_text.md', 'skip_this.md', 'ignore_sample.mdx']

ZWNJ = '\u200C'
PLAIN = '**'
WRAPPED = f'{ZWNJ}{PLAIN}{ZWNJ}'


def wrap_zwnj_once(text: str) -> str:
    pattern = re.compile(rf'(?<!{ZWNJ}){re.escape(PLAIN)}(?!{ZWNJ})')
    return pattern.sub(WRAPPED, text)


def process_file(path: str) -> bool:
    bak = path + '_bk'
    try:
        shutil.copy2(path, bak)
    except Exception as e:
        print(f'Backup failed: {e}', file=sys.stderr)
        return False
    try:
        raw = open(path, 'r', encoding='utf-8').read()
    except Exception as e:
        print(f'Read failed: {e}', file=sys.stderr)
        return False
    count = raw.count(PLAIN)
    if count % 2 != 0:
        print(f'Warning: odd PLAIN count {count}', file=sys.stderr)
    result = wrap_zwnj_once(raw)
    try:
        open(path, 'w', encoding='utf-8').write(result)
    except Exception as e:
        print(f'Write failed: {e}', file=sys.stderr)
        return False
    return True

class ZwnjGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ZWNJ Wrapper GUI')
        self.resize(600, 400)
        self.setAcceptDrops(True)

        self.list_widget = QListWidget()
        self.info_label = QLabel('ファイルをドラッグ＆ドロップしてください')

        self.convert_btn = QPushButton('変換')
        self.convert_btn.clicked.connect(self.on_convert)

        layout = QVBoxLayout(self)
        layout.addWidget(self.info_label)
        layout.addWidget(self.list_widget)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.convert_btn)
        layout.addLayout(btn_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            # *.md, *.mdx のみ登録かつ除外リストにない
            basename = os.path.basename(path)
            if (os.path.isfile(path)
                    and path.lower().endswith(('.md', '.mdx'))
                    and basename not in IGNORE_LIST):
                existing = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
                if path not in existing:
                    self.list_widget.addItem(path)
        self.info_label.setText('ファイルを登録しました')

    def on_convert(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            text = item.text()
            # basename抽出
            path = text.split(':', 1)[-1] if ':' in text else text
            basename = os.path.basename(path)
            # 除外ファイルはスキップ
            if basename in IGNORE_LIST:
                continue
            # 再変換時はエラーのもののみ、初回は全て
            if text.startswith('正常終了:'):
                continue
            success = process_file(path)
            if success:
                item.setText(f'正常終了:{path}')
            else:
                item.setText(f'エラー:{path}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ZwnjGUI()
    gui.show()
    sys.exit(app.exec_())
