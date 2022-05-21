#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,cv2
import numpy as np

from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QLabel,QPushButton,QFrame,QHBoxLayout,QVBoxLayout,QComboBox)
from PySide6.QtGui import QPixmap,QImage,QIcon
from PySide6.QtCore import Qt,QThread,Signal,Slot

style_sheet="""
    QLabel#VideoLabel{
        color:darkgrey;
        border: 2px solid darkgrey;
        qproperty-alignment:AlignCenter;
        }
    """

class VideoThread(QThread):
    frame_data_update=Signal(np.ndarray)
    def __init__(self,parent,video_file=None):
        super().__init__()
        self.parent=parent
        self.video_file=video_file

    def run(self):
        self.capture=cv2.VideoCapture(self.video_file)
        

        while self.parent.thread_is_running:
            ret_val,frame=self.capture.read()

            if not ret_val:
                break   #An Error occured when try to open the end video

            else:
                frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                #Resize an image for faster detection

                frame=cv2.resize(frame,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA)
                rects=self.createHOGDescriptor(frame)

                for (x_tr,y_tr,x_br,y_br) in rects:
                    frame=cv2.rectangle(frame,(x_tr,y_tr),(x_br,y_br),(0,0,255),2)
                self.frame_data_update.emit(frame)
    def createHOGDescriptor(self,frame):
        '''Function creates the HOG Descriptor for human detection ans returns the detections(rects)'''
        hog=cv2.HOGDescriptor()

        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        rects,weigths=hog.detectMultiScale(frame,winStride=(4,4),padding=(8,8),scale=1.1)

        rects=np.asarray([[x,y,x+width,y+height] for (x,y,width,height) in rects])
        return rects
    def stop_thread(self):
        self.wait()
        self.terminate()
class DisplayVideo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()
    def initializeUI(self):
        self.setMinimumSize(800,500)
        self.setWindowTitle("Human Detection GUİ")
        self.thread_is_running=False
        self.setupWindow()
        self.show()

    def setupWindow(self):
        self.video_display_label=QLabel()
        self.video_display_label.setObjectName("VideoLabel")

        #Test Algrithme comboxBox
        algo=["HOG","Test2","Test3","Test3"]
        self.algorithm=QComboBox()
        for item in algo:
            self.algorithm.addItem(item)

        #Start button declaration
        self.start_button=QPushButton("Video Start")
        pixmap=QPixmap("images/start-48.png")
        start_icon=QIcon(pixmap)
        self.start_button.setIcon(start_icon)
        self.start_button.setIconSize(pixmap.rect().size())
        self.start_button.clicked.connect(self.start_video)

        #Stop button declaration
        self.stop_button=QPushButton("Stop Video")
        pixmap=QPixmap("images/stop-48.png")
        stop_icon=QIcon(pixmap)
        self.stop_button.setIcon(stop_icon)
        self.stop_button.setIconSize(pixmap.rect().size())
        self.stop_button.clicked.connect(self.stop_video)

        #Capture frame image button
        
        self.capture_button=QPushButton("Capture Frame")
        pixmap=QPixmap("images/screenshot-48.png")
        capture_icon=QIcon(pixmap)
        self.capture_button.setIcon(capture_icon)
        self.capture_button.setIconSize(pixmap.rect().size())
        #self.cpature_button.clicked.connect(self.stop_video)

        #Create horizontal and vertical layouts

        side_panel_v_box=QVBoxLayout()
        side_panel_v_box.setAlignment(Qt.AlignTop)
        side_panel_v_box.addWidget(self.algorithm)
        side_panel_v_box.addWidget(self.start_button)
        side_panel_v_box.addWidget(self.stop_button)
        side_panel_v_box.addWidget(self.capture_button)

        side_panel_frame=QFrame()
        side_panel_frame.setMinimumWidth(200)
        side_panel_frame.setLayout(side_panel_v_box)

        main_h_box=QHBoxLayout()
        main_h_box.addWidget(self.video_display_label,1)
        main_h_box.addWidget(side_panel_frame)

        #Create container widget and set main window's widget

        container=QWidget()
        container.setLayout(main_h_box)
        self.setCentralWidget(container)
    def start_video(self):
        self.thread_is_running=True
        self.start_button.setEnabled(False)
        self.start_button.repaint()
        video_file="images/people.mp4"
        self.video_thread_work=VideoThread(self,video_file)
        self.video_thread_work.frame_data_update.connect(self.update_video_frame)
        self.video_thread_work.start()
    def stop_video(self):
        if self.thread_is_running==True:
            self.thread_is_running=False
            self.video_thread_work.stop_thread()
            self.video_display_label.clear()
            self.start_button.setEnabled(True)
    def update_video_frame(self,video_frame):
        h,w,channels=video_frame.shape
        bytes_per_line=w*channels
        convert_to_qt_image=QImage(video_frame,w,h,bytes_per_line,QImage.Format_RGB888)
        self.video_display_label.setPixmap(QPixmap.fromImage(convert_to_qt_image).scaled(self.video_display_label.width(),self.video_display_label.height(),Qt.KeepAspectRatioByExpanding))

    def close_event(self):
       pass 


if __name__=='__main__':

    app=QApplication()
    app.setStyleSheet(style_sheet)
    w=DisplayVideo()
    sys.exit(app.exec())


