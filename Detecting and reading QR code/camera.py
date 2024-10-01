from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt,QTimer
from pyzbar.pyzbar import decode
from PyQt5 import uic 
import numpy as np
import cv2
import sys


class Camera_Ui(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("camera.ui", self)
        self.setWindowTitle("Camera")

        self.is_live = False

        
        self.scene = QGraphicsScene()  
        self.graphicsView.setScene(self.scene)

        #...........................
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)


        self.graphicsView = self.findChild(QGraphicsView, "graphicsView")
        self.btn_Live = self.findChild(QPushButton, "btn_Live")
        self.btn_Trigger = self.findChild(QPushButton, "btn_Trigger")
        self.btn_Saveimage = self.findChild(QPushButton, "btn_Saveimage")
        self.btn_Loadimage = self.findChild(QPushButton, "btn_Loadimage")
        self.btn_Loadvideo = self.findChild(QPushButton, "btn_Loadvideo")
        self.frame_oke_ng = self.findChild(QLabel, "frame_oke_ng")
        self.Text_Content_Code = self.findChild(QTextEdit, "Text_Content_Code")

        self.btn_Live.clicked.connect(self.toggle_live)
        self.btn_Trigger.clicked.connect(self.capture_image)
        self.btn_Saveimage.clicked.connect(self.save_image)
        self.btn_Loadimage.clicked.connect(self.load_image)
        self.btn_Loadvideo.clicked.connect(self.load_video)
       # self.frame_oke_ng.set("background-color: yellow;")

    def toggle_live(self):
        if not self.is_live:
            self.is_live = True
            self.btn_Live.setText("STOP")
            self.capture = cv2.VideoCapture(0)
            self.timer.start(5)
        else:
            self.is_live = False
            self.btn_Live.setText("LIVE")
            self.timer.stop()
            self.scene.clear()
            #self.frame_oke_ng.setStyleSheet("background-color: yellow;")
    def capture_image(self):
        if not self.is_live:
            ret, frame = self.capture.read()
            if ret:
                self.read_barcode(frame)
                self.update_graphics_view(self.scene, frame)
    def save_image(self):
        if not self.is_live:
            if self.scene.items():
                file_dialog = QFileDialog()
                file_path, _ = file_dialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
                if file_path:
                    pixmap = self.scene.items()[0].pixmap()
                    pixmap.save(file_path)
            else:
                print("No image to save")
    def load_image(self):
        if not self.is_live:
            file_dialog = QFileDialog()
            file_path = file_dialog.getOpenFileName(self, "LOad Image", "", "Images (*.png *.jpg *.jpeg);;All Files (*.*)")[0]
            if file_path:
                image = cv2.imread(file_path)
                self.update_graphics_view(self.scene, image)
    def load_video(self):
        if not self.is_live:
            file_dialog = QFileDialog()
            file_path = file_dialog.getOpenFileName(self, "Load Video", "", "Video Files (*.mp4 *.avi *.mov);;All Files (*.*)")[0]
            if file_path:
                self.capture = cv2.VideoCapture(file_path)
                self.timer=QTimer(self)
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(70)
    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.read_barcode(frame)
            self.update_graphics_view(self.scene, frame)
    def update_graphics_view(self, graphics_view, frame):
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        graphics_view.clear()
        graphics_view.addPixmap(QPixmap.fromImage(q_image))

    def read_barcode(self, frame):
        decoded_objects = decode(frame)
        self.Text_Content_Code.setPlainText("")
        #self.frame_oke_ng.setStyleSheet("background-color: red;") 
        for obj in decoded_objects:
            data = obj.data.decode("utf-8")
            self.Text_Content_Code.setPlainText(data)
            # if self.Text_Content_Code.toPlainText() != "":
            #     self.frame_oke_ng.setStyleSheet("background-color: green;")
            rect_points = obj.polygon
            if len(rect_points) > 4:
                hull =cv2.convexHull(np.array([point for point in rect_points], dtype=np.float32))
                cv2.polylines(frame, [hull], isClosed=True, color= (0, 255, 0), thickness=2)
            else:
                cv2.polylines(frame, [np.array(rect_points,dtype=np.int32)], isClosed=True, color= (0, 255, 0), thickness=2)
            

            cv2.putText(frame, data, (rect_points[0][0], rect_points[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
             
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = Camera_Ui()
    MainWindow.show()
    sys.exit(app.exec_())

