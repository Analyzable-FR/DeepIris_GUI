'''
MIT License

Copyright (c) 2023 Analyzable

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import os
import sys

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFileDialog, QApplication, QMainWindow, QSplashScreen
from PySide6.QtCore import QFile, QTimer, Qt
from window import Window
from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.loadUi()
        self.ui.actionOpen.triggered.connect(self.openImage)
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionExport.triggered.connect(self.export)

    def loadUi(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def openImage(self):
        filename, __ = QFileDialog.getOpenFileName(self, self.tr(
            "Open Image"), "/home/Pictures", self.tr(""))
        if filename:
            self.newWindow(filename)

    def newWindow(self, path):
        window = Window(path)
        self.ui.mdiArea.addSubWindow(window)
        window.show()

    def export(self):
        if (subWindow := self.ui.mdiArea.activeSubWindow()) is not None:
            filename, __ = QFileDialog.getSaveFileName(self, self.tr(
                "Export Image"), "/home/", self.tr("Images (*.tiff"))
            if filename:
                if (i := os.path.splitext(filename))[-1] != ".tiff":
                    filename = i[0] + ".tiff"
                subWindow.exportImage(filename)

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            self.newWindow(mimeData.urls()[0].toLocalFile())

    def dragEnterEvent(self, event):
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication([])
    app.setApplicationName("DeepIris")
    app.setApplicationVersion("0.0.1")
    app.setOrganizationName("Analyzable")
    app.setOrganizationDomain("cc.gallois")
    app.setWindowIcon(QIcon(":/logo.png"))
    splash = QSplashScreen(QPixmap(":/logo.png").scaled(500, 500))
    splash.showMessage("Build number {} by Analyzable".format(app.applicationVersion()), color=Qt.black,
                       alignment=Qt.AlignLeft | Qt.AlignBottom)
    widget = MainWindow()
    splash.show()
    QTimer.singleShot(2000, splash.close)
    widget.show()
    sys.exit(app.exec())
