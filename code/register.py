import json
from PyQt6.QtWidgets import QMessageBox #Lớp QMessageBox để hiển thị thông báo cho người dùng
from PyQt6.QtWidgets import QMainWindow #Lớp QMainWindow để tạo cửa sổ cho ứng dụng
from PyQt6 import uic

class Register(QMainWindow): #Kế thừa các thuộc tính và phương thức từ QMainWindow
    def __init__(self): #Hàm init tự động chạy khi khởi tạo đối tượng
        super().__init__() #super giúp gọi hàm init của QMainWindow
        uic.loadUi("./gui/register.ui", self)
        self.btn_register.clicked.connect(self.xu_ly_dang_ky)
        self.homewindow = None
        self.btn_areadyLogin.clicked.connect(self.Home)
    def xu_ly_dang_ky(self):
        txtUsername = self.txtUsername.text().strip()
        txtpass = self.txtpass.text().strip()
        txtRepass = self.txtRepass.text().strip()
        
        if txtUsername == "" or txtpass == "" or txtRepass == "":
            self.thongBao("Thông báo", "Vui lòng nhập đầy đủ thông tin")
            return
        
        if txtpass != txtRepass:
            self.thongBao("Thông báo", "Mật khẩu không trùng khớp")
            return
        
        with open("code/account.json", "r") as file:
            data = json.load(file)
            
        for item in data["accounts"]:
            if item["username"] == txtUsername:
                self.thongBao("Thông báo", "Tài khoản đã tồn tại")
                return
            
        data["accounts"].append(dict(username = txtUsername, password = txtpass,balance = 0))
        with open("code/account.json", "w") as file:
            json.dump(data, file, indent=4)
            self.thongBao("Thông báo", "Đăng ký tài khoản thành công")
        self.Home()
        
    def thongBao(self, tieuDe, noiDung):
                message = QMessageBox()  
                message.setIcon(QMessageBox.Icon.Question)
                message.setWindowTitle(tieuDe)
                message.setText(noiDung)
                message.exec()
    def Home(self):
        from login import Login
        if self.homewindow == None:
         self.homewindow = Login()
        self.homewindow.show()
        self.hide()

        # self.txtUsername.clear()




