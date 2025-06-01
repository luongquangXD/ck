from PyQt6.QtWidgets import QMessageBox #Lớp QMessageBox để hiển thị thông báo cho người dùng
from PyQt6.QtWidgets import QMainWindow #Lớp QMainWindow để tạo cửa sổ cho ứng dụng
from PyQt6 import uic
import json #Thư viện json để đọc và ghi dữ liệu JSON

class Login(QMainWindow): #Kế thừa các thuộc tính và phương thức từ QMainWindow
    def __init__(self): #Hàm init tự động chạy khi khởi tạo đối tượng
        super().__init__() #super giúp gọi hàm init của QMainWindow
        uic.loadUi("./gui/login.ui", self)
        self.btn_login.clicked.connect(self.xu_ly_dang_nhap)
        self.homewindow = None
        self.btn_reg.clicked.connect(self.Register)

    def xu_ly_dang_nhap(self):
        """Xử lý đăng nhập bằng cách kiểm tra thông tin tài khoản"""
        username = self.txtUsername.text()
        password = self.txtpass.text()

        try:
            # Đọc file JSON chứa danh sách tài khoản
            with open("code/account.json", "r") as file:
                data = json.load(file)

            # Duyệt qua tất cả các tài khoản trong danh sách
            for account in data["accounts"]:
                if account["username"] == username and account["password"] == password:
                    # Nếu thông tin đúng, lưu tài khoản hiện tại vào file current_account.json
                    with open("code/current_account.json", "w") as file:
                        json.dump({"current_account": username}, file, indent=4)

                    # Mở cửa sổ Home
                    from Homepage import Home
                    self.homewindow = Home()
                    self.homewindow.show()
                    self.close()
                    return

            # Nếu không tìm thấy tài khoản phù hợp
            QMessageBox.critical(self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
        except FileNotFoundError:
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy file account.json")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Lỗi", "File account.json bị lỗi định dạng")
    def Register(self):
        from register import Register
        if self.homewindow == None:
            self.homewindow = Register()
        self.homewindow.show()
        self.close()
        return
