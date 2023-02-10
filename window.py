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


from PySide6.QtWidgets import QInputDialog, QLineEdit, QWidget, QSplashScreen, QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem, QStyleFactory, QMenu
from PySide6.QtCore import QStandardPaths, QDir, QEvent, Signal, Slot, Qt, QPoint, QThread, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QCursor, QKeySequence, QAction, QActionGroup
import cv2
import os
import rawpy
import numpy as np
from deepiris.predict import QDetector

from imageviewer import ImageViewer


class Window(QMdiSubWindow):

    statusChanged = Signal(str)
    progressChanged = Signal(bool)

    def __init__(self, path, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.path = path
        self.setWindowTitle(os.path.basename(self.path))
        self.imageViewer = ImageViewer(parent=self)
        self.imageViewer.isDrawable = False
        self.setWidget(self.imageViewer)
        self.detector = QDetector()  # no parent to be moved on a QThread
        self.detector.imageChanged.connect(self.updateImage)
        self.detector.statusChanged.connect(self.statusChanged)
        self.readImage()

    def readImage(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if os.path.splitext(self.path)[1] in [".NEF", ".RAW"]:
                with rawpy.imread(self.path) as raw:
                    self.image = raw.postprocess(output_bps=16, use_camera_wb=True,
                                                 use_auto_wb=False, output_color=rawpy.ColorSpace.Adobe)
                    self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2RGBA)
            else:
                self.image = cv2.imread(self.path, -1)
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGBA)
            self.imageViewer.setImage(self.image)
            self.detector.setImage(self.image)
        except Exception as e:
            print(e)
        finally:
            QApplication.restoreOverrideCursor()

    def exportImage(self, filename):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            cv2.imwrite(filename, self.image)
        except Exception as e:
            print(e)
        finally:
            QApplication.restoreOverrideCursor()

    def updateImage(self, image):
        self.image = np.copy(image)
        self.imageViewer.setImage(self.image)

    def processImage(self):
        try:
            self.processingThread = QThread(self)
            self.detector.moveToThread(self.processingThread)
            self.processingThread.started.connect(self.detector.process)
            self.detector.finished.connect(self.processingThread.quit)
            self.detector.finished.connect(
                lambda: self.progressChanged.emit(False))
            self.processingThread.finished.connect(
                self.processingThread.deleteLater)
            self.progressChanged.emit(True)
            self.processingThread.start()
        except Exception as e:
            print(e)
