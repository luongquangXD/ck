import json
from PyQt6.QtWidgets import QMessageBox #Lớp QMessageBox để hiển thị thông báo cho người dùng
from PyQt6.QtWidgets import QMainWindow #Lớp QMainWindow để tạo cửa sổ cho ứng dụng
from PyQt6.QtWidgets import QWidget,QLineEdit,QApplication
from PyQt6 import uic
import webbrowser
import re
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QEvent, QPropertyAnimation, QEasingCurve, QPoint

class GlowButtonMixin:
    def enable_glow(self, color=QColor(0,255,255), blur=20):
        self.setMouseTracking(True)
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setColor(color)
        self.glow_effect.setBlurRadius(blur)
        self.glow_effect.setOffset(0)
        self.setGraphicsEffect(None)
        self.installEventFilter(self)
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Enter:
            effect = QGraphicsDropShadowEffect()
            effect.setColor(QColor(255, 200, 0, 255))  # Vàng cam đậm, rõ nét
            effect.setBlurRadius(20)  # Viền sắc nét hơn
            effect.setOffset(0)
            self.setGraphicsEffect(effect)
            self._current_effect = effect  # Giữ tham chiếu mạnh
        elif event.type() == QEvent.Type.Leave:
            self.setGraphicsEffect(None)
            self._current_effect = None
        return False

class Home(QMainWindow): # Kế thừa các thuộc tính và phương thức từ QMainWindow
    def __init__(self): # Hàm init tự động chạy khi khởi tạo đối tượng
        super().__init__() # super giúp gọi hàm init của QMainWindow
        uic.loadUi("./gui/home.ui", self)
        
        self.current_account = None  # Thuộc tính để lưu tài khoản hiện tại
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)
        
        # Kết nối các nút với hiệu ứng chuyển tab
        self.btn_account.clicked.connect(lambda: self.slide_to_page(1))
        self.btn_inf.clicked.connect(lambda: self.slide_to_page(2))
        self.btn_balance.clicked.connect(lambda: self.slide_to_page(1))
        self.btn_exit2.clicked.connect(lambda: self.slide_to_page(0))
        self.btn_exit2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_setting.clicked.connect(lambda: self.slide_to_page(3))
        self.btn_home.clicked.connect(lambda: self.slide_to_page(0) if self.stackedWidget_2.currentIndex() != 0 else None)
        
        # Các kết nối khác giữ nguyên
        self.btn_account.clicked.connect(self.show_balance)
        self.btn_account.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btn_inf.clicked.connect(self.show_information)
        self.edit_balance.clicked.connect(self.Edit_balance)
        self.done_edit.clicked.connect(self.Edit_balance_finnal)
        self.ckb_showpass.clicked.connect(self.show_password)
        self.btn_exit.clicked.connect(self.exit)
        self.btn_change_theme.clicked.connect(self.change_theme)
        self.btn_change_theme.clicked.connect(lambda: self.apply_theme("code/dark_theme.qss"))
        self.btn_link.clicked.connect(self.open_link)
        self.gemini_btn.clicked.connect(self.Gemini)

        
        # Tự động xác định tài khoản hiện tại
        self.set_current_account()

        # Thêm hiệu ứng phát sáng cho các nút
        for btn_name in [
            'btn_account','btn_inf','btn_balance','btn_exit2','edit_balance','done_edit',
            'btn_exit','btn_change_theme','btn_setting','btn_home','btn_link','gemini_btn']:
            btn = getattr(self, btn_name, None)
            if btn is not None:
                # Thêm mixin cho từng nút
                btn.__class__ = type('GlowButton', (btn.__class__, GlowButtonMixin), {})
                btn.enable_glow(QColor(255,200,0,255), 20)

    def set_current_account(self):
        #"""Phương thức để tự động xác định tài khoản hiện tại"""
        try:
            with open("code/current_account.json", "r") as file:
                current_account_name = json.load(file).get("current_account")
                print(current_account_name)
            
            with open("code/account.json", "r") as file:
                data = json.load(file)
                for account in data["accounts"]:
                    if account["username"] == current_account_name:
                        self.current_account = account["username"]
                        print(self.current_account)
                        return
            
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy tài khoản hiện tại!")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {e}")

    def show_balance(self):
        with open("code/account.json", "r") as file:
            data = json.load(file)
            for account in data["accounts"]:
                if account["username"] == self.current_account:
                    account["balance"] = str(account["balance"])  # Chuyển đổi số dư thành chuỗi
                    self.txt_balance.setText(account["balance"])
                    print(str(account["balance"]))
                    return
    def Edit_balance(self):
        self.txt_balance.setReadOnly(False)
    def Edit_balance_finnal(self):
            with open("code/account.json", "r") as file:
                data = json.load(file)

            # Cập nhật số dư cho tài khoản hiện tại
            for account in data["accounts"]:
                if account["username"] == self.current_account:
                    new_balance = self.txt_balance.text()
                    new_balance = new_balance.replace(' ', '')
                    new_balance = new_balance.lstrip('0')
                    new_balance = re.sub(r'\D', '', new_balance)
                    account["balance"] = new_balance  # Lưu dưới dạng chuỗi
                    self.txt_balance.setReadOnly(True)
                    self.txt_balance.setText(new_balance)
                        
            
            # Ghi lại file JSON
            with open("code/account.json", "w") as file:
                json.dump(data, file, indent=4)
            self.txt_balance.setReadOnly(True)
            return
    def show_information(self):
        with open("code/account.json", "r") as file:
            data = json.load(file)
            for account in data["accounts"]:
                if account["username"] == self.current_account:
                    self.txt_username.setText(account["username"])
                    self.txt_pass.setText(account["password"])
                    return
    def show_password(self):
        if self.ckb_showpass.isChecked():
            self.txt_pass.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
    def exit(self):
        from login import Login
        self.homewindow = Login()
        self.homewindow.show()
        self.close()
        return

    def apply_theme(self, theme_file):
        """Áp dụng theme từ file QSS"""
        try:
            with open(theme_file, "r", encoding="utf-8") as file:  # Đọc file với mã hóa UTF-8
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print(f"Không tìm thấy file theme: {theme_file}")
        except UnicodeDecodeError as e:
            print(f"Lỗi mã hóa khi đọc file theme: {e}")
    def change_theme(self):
        """Chuyển đổi giữa theme sáng và tối"""
        self.apply_theme("code/dark_theme.qss")  # Chuyển sang theme tối
    def open_link(self):
        webbrowser.open('https://www.freeprivacypolicy.com/live/71f463bb-65ad-4e2e-8c53-166ab46cb767')
    def Gemini(self):
        from Chatbotgemini import GeminiChatbot
        self.chatbot_window = GeminiChatbot()
        self.chatbot_window.show()
        return

    def slide_to_page(self, index):
        # Lấy widget hiện tại và widget đích
        current_widget = self.stackedWidget_2.currentWidget()
        target_widget = self.stackedWidget_2.widget(index)
        
        # Tạo animation cho widget hiện tại
        self.animation_out = QPropertyAnimation(current_widget, b"pos")
        self.animation_out.setDuration(600)
        self.animation_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_out.setStartValue(QPoint(0, 0))
        self.animation_out.setEndValue(QPoint(-self.width(), 0))
        
        # Tạo animation opacity cho widget hiện tại
        self.fade_out = QPropertyAnimation(current_widget, b"windowOpacity")
        self.fade_out.setDuration(600)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        
        # Chuẩn bị widget đích
        target_widget.setGeometry(self.width(), 0, self.width(), self.height())
        target_widget.setWindowOpacity(0.0)
        
        # Tạo animation cho widget đích
        self.animation_in = QPropertyAnimation(target_widget, b"pos")
        self.animation_in.setDuration(600)
        self.animation_in.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_in.setStartValue(QPoint(self.width(), 0))
        self.animation_in.setEndValue(QPoint(0, 0))
        
        # Tạo animation opacity cho widget đích
        self.fade_in = QPropertyAnimation(target_widget, b"windowOpacity")
        self.fade_in.setDuration(600)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        
        # Kết nối các animation
        self.animation_out.finished.connect(self.animation_in.start)
        self.fade_out.finished.connect(self.fade_in.start)
        self.fade_in.finished.connect(lambda: self.stackedWidget_2.setCurrentIndex(index))
        
        # Bắt đầu animation
        self.animation_out.start()
        self.fade_out.start()


           





