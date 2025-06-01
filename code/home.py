from PyQt6.QtWidgets import QApplication #Cần QApplication để tạo 1 ứng dụng mới
from PyQt6.QtWidgets import QMainWindow
from login import Login
import sys


if __name__ == '__main__': #Chỉ khởi chạy khi đây là file gốc
    app = QApplication(sys.argv) #Khởi tạo ứng dụng
    window = Login()
    window.show() #Hàm show() để mở cửa sổ register
    app.exec() #hàm exec() để khởi chạy ứng dụng

