import cv2
import numpy as np
from PyQt5.QtCore import QDir, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout, QPushButton

from libs.VideoThread import VideoThread


class ViewPort(QWidget):

    def on_browse_video(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Single File', QDir.rootPath(), '*.mp4')
        self.on_set_video(path)

    def on_update_params(self, counter):
        self.counter.setText(str(counter))

    def on_set_video(self, path):
        self.thread = VideoThread(path, self.on_update_params)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCV in PyQt5")
        window = QHBoxLayout()

        self.viewport = QLabel()
        self.disply_width = 640
        self.display_height = 480
        self.viewport.setFixedSize(self.disply_width, self.display_height)

        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignTop)

        self.counter = QLabel()
        self.counter.setText("0")
        sidebar.addWidget(self.counter)

        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self.on_browse_video)
        sidebar.addWidget(select_file_button)

        window.addWidget(self.viewport)
        window.addLayout(sidebar)

        self.setLayout(window)

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.viewport.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
