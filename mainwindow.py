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

from PySide6.QtGui import QBrush, QActionGroup, QIcon, QPixmap, QAction, QKeySequence
from PySide6.QtWidgets import QMdiArea, QMenu, QMessageBox, QProgressBar, QFileDialog, QApplication, QMainWindow, QSplashScreen
from PySide6.QtCore import QFile, QTimer, Qt
from window import Window
from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.loadUi()
        self.setWindowTitle("DeepIris Demo")
        self.ui.actionOpen.triggered.connect(self.openImage)
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionExport.triggered.connect(self.export)

        self.ui.mdiArea.setBackground(QBrush(QPixmap(":/demo.png")))

        processAction = QAction(QIcon(":/crop.png"),
                                self.tr("Crop iris and reduce pupil"), self)
        processAction.triggered.connect(self.process)
        self.ui.toolBar.addAction(processAction)

        centerAction = QAction(QIcon(":/center.png"),
                               self.tr("Center pupil"), self)
        centerAction.setEnabled(False)
        self.ui.toolBar.addAction(centerAction)

        settingsAction = QAction(QIcon(":/settings.png"),
                                 self.tr("Settings"), self)
        settingsAction.setEnabled(False)
        self.ui.toolBar.addAction(settingsAction)

        viewMenu = QMenu(self.tr("View Mode"), self)
        self.ui.menuView.addMenu(viewMenu)
        viewMode = QActionGroup(self)
        stackView = QAction(self.tr("&Tabbed"), self)
        stackView.setCheckable(True)
        stackView.toggled.connect(
            lambda i: self.ui.mdiArea.setViewMode(QMdiArea.TabbedView))
        viewMode.addAction(stackView)
        viewMenu.addAction(stackView)
        winView = QAction(self.tr("&Windowed"), self)
        winView.setCheckable(True)
        winView.toggled.connect(
            lambda i: self.ui.mdiArea.setViewMode(QMdiArea.SubWindowView))
        viewMode.addAction(winView)
        viewMenu.addAction(winView)
        stackView.setChecked(True)

        winMenu = QMenu(self.tr("Windows reordering"), self)
        self.ui.menuView.addMenu(winMenu)
        cascadeView = QAction(self.tr("&Cascaded"), self)
        cascadeView.setShortcut(QKeySequence("Ctrl+X"))
        cascadeView.triggered.connect(self.ui.mdiArea.cascadeSubWindows)
        winView.toggled.connect(winMenu.setEnabled)
        winMenu.addAction(cascadeView)
        tileView = QAction(self.tr("&Tiled"), self)
        tileView.triggered.connect(self.ui.mdiArea.tileSubWindows)
        tileView.setShortcut(QKeySequence("Ctrl+B"))
        winView.toggled.connect(winMenu.setEnabled)
        winMenu.addAction(tileView)
        winMenu.setEnabled(False)

        self.ui.actionAboutQt.triggered.connect(qApp.aboutQt)
        self.ui.actionAboutMe.triggered.connect(self.about)

        self.progressBar = QProgressBar(self)
        self.ui.statusbar.addPermanentWidget(self.progressBar)
        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(0)

    def showProgress(self, isVisible):
        self.progressBar.setVisible(isVisible)

    def loadUi(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def openImage(self):
        filename, __ = QFileDialog.getOpenFileName(self, self.tr(
            "Open Image"), "/home/Pictures", self.tr("Images RAW or Raster ()"))
        if filename:
            self.newWindow(filename)

    def newWindow(self, path):
        window = Window(path)
        window.statusChanged.connect(self.ui.statusbar.showMessage)
        window.progressChanged.connect(self.showProgress)
        self.ui.mdiArea.addSubWindow(window)
        window.show()

    def process(self):
        if (subWindow := self.ui.mdiArea.activeSubWindow()) is not None:
            subWindow.processImage()

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

    def about(self):
        messageBox = QMessageBox(self)
        messageBox.setWindowTitle(self.tr("About"))
        messageBox.setText(self.tr(
            "DeepIris is designed by <a href='https://gallois.cc'>Analyzable</a>. Custom computer vision solution powered by open-source technologies."))
        messageBox.setIconPixmap(QPixmap(":/analyzable.png"))
        messageBox.exec()


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
