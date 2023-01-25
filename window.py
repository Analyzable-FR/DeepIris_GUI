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
import numpy as np
from deepiris.predict import QDetector

from imageviewer import ImageViewer


class Window(QMdiSubWindow):

    def __init__(self, path, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.path = path
        self.setWindowTitle(os.path.basename(self.path))
        self.imageViewer = ImageViewer(parent=self)
        self.imageViewer.isDrawable = False
        self.setWidget(self.imageViewer)
        self.detector = QDetector(self)
        self.detector.imageChanged.connect(self.updateImage)
        self.readImage()

    def readImage(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
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
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.detector.process()
        except Exception as e:
            print(e)
        finally:
            QApplication.restoreOverrideCursor()
