from time import sleep

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal


def get_centrolid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1
    return cx, cy


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, file: str, on_update_params):
        super().__init__()
        self.file = file
        self.on_update_params = on_update_params

    def run(self):
        cap = cv2.VideoCapture(self.file)
        fps = cap.get(cv2.CAP_PROP_FPS)

        min_contour_width = 80
        min_contour_height = 80
        offset = 8
        line_height = 550
        matches = []
        cars = 0

        _, frame1 = cap.read()
        ret, frame2 = cap.read()

        while ret:
            d = cv2.absdiff(frame1, frame2)
            grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

            blur = cv2.GaussianBlur(grey, (3, 3), 0)

            ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(th, np.ones((5, 5)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

            closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
            contours, h = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for (i, c) in enumerate(contours):
                (x, y, w, h) = cv2.boundingRect(c)
                contour_valid = (w >= min_contour_width) and (h >= min_contour_height)

                if not contour_valid:
                    continue

                cv2.rectangle(frame1, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)

                cv2.line(frame1, (0, line_height), (1200, line_height), (0, 255, 0), 2)
                centrolid = get_centrolid(x, y, w, h)
                matches.append(centrolid)
                cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
                for (x, y) in matches:
                    if y < (line_height + offset) and y > (line_height - offset):
                        cars += 1
                        matches.remove((x, y))
                        cv2.line(frame1, (0, line_height), (1200, line_height), (0, 0, 255), 2)

            self.on_update_params(cars)
            self.change_pixmap_signal.emit(frame1)

            frame1 = frame2
            ret, frame2 = cap.read()
            sleep(1 / fps)
