import json
from PyQt6.QtWidgets import QMessageBox #Lớp QMessageBox để hiển thị thông báo cho người dùng
from PyQt6.QtWidgets import QMainWindow #Lớp QMainWindow để tạo cửa sổ cho ứng dụng
from PyQt6.QtWidgets import QWidget,QLineEdit,QApplication, QComboBox, QDateEdit
from PyQt6 import uic
import webbrowser
import re
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QEvent, QPropertyAnimation, QEasingCurve, QPoint, QDate
import sqlite3
from datetime import datetime

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
        
        # Initialize product types
        self.product_types = [
            "Laptop",
            "Desktop",
            "Smartphone",
            "Tablet",
            "Accessories",
            "Monitor",
            "Printer",
            "Network Device",
            "Storage Device",
            "Other"
        ]
        
        # Setup product type comboboxes
        self.setup_product_type_comboboxes()
        
        # Setup date pickers
        self.setup_date_pickers()
        
        # Initialize database
        self.init_database()
        
        # Connect CRUD buttons with debug prints
        print("Connecting CRUD buttons...")
        self.pushButton.clicked.connect(lambda: print("ADD button clicked"))
        self.pushButton.clicked.connect(self.show_add_page)
        self.pushButton_2.clicked.connect(self.delete_product)
        self.pushButton_3.clicked.connect(self.show_edit_page)
        self.pushButton_4.clicked.connect(self.save_new_product)
        self.pushButton_5.clicked.connect(self.save_edit_product)
        print("CRUD buttons connected")
        
        # Load initial products
        self.load_products()
        
        # Kết nối các nút với hiệu ứng chuyển tab
        self.btn_account.clicked.connect(lambda: self.slide_to_page(1))
        self.btn_inf.clicked.connect(lambda: self.slide_to_page(2))
        self.btn_balance.clicked.connect(lambda: self.slide_to_page(1))
        self.btn_exit2.clicked.connect(lambda: self.slide_to_page(0))
        self.btn_exit2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_setting.clicked.connect(lambda: self.slide_to_page(3))
        self.btn_home.clicked.connect(lambda: self.slide_to_page(0) if self.stackedWidget_2.currentIndex() != 0 else None)
        self.btn_multi.clicked.connect(lambda: self.slide_to_page(4))
        
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
        self.btn_X.clicked.connect(self.open_link_X)
        self.btn_git.clicked.connect(self.open_link_git)
        
        # Tự động xác định tài khoản hiện tại
        self.set_current_account()

        # Thêm hiệu ứng phát sáng cho các nút
        for btn_name in [
            'btn_account','btn_inf','btn_balance','btn_exit2','edit_balance','done_edit',
            'btn_exit','btn_change_theme','btn_setting','btn_home','btn_link','gemini_btn','btn_X','btn_git']:
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
    def open_link_X(self):
        webbrowser.open('https://x.com/quang16062k11')
    def open_link_git(self):
        webbrowser.open('https://github.com/luongquangXD')
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

    def init_database(self):
        """Initialize the database and create table if not exists"""
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT UNIQUE,
                product_type TEXT,
                product_name TEXT,
                manufacturer TEXT,
                production_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_products(self):
        """Load all products into the list widget"""
        self.listWidget.clear()
        conn = sqlite3.connect("techshop.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()

        for product in products:
            self.listWidget.addItem(
                f"Code: {product[1]} | Type: {product[2]} | Name: {product[3]} | "
                f"Manufacturer: {product[4]} | Date: {product[5]}"
            )

    def show_edit_page(self):
        """Switch to edit product page"""
        try:
            current_item = self.listWidget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "Please select a product to edit!")
                return

            self.slide_to_page(6)  # Changed from 5 to 6 for EDIT page
            product_code = current_item.text().split("|")[0].split(":")[1].strip()
            
            # Load product data into edit fields
            conn = sqlite3.connect("techshop.db")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE product_code = ?', (product_code,))
            product = cursor.fetchone()
            conn.close()

            if product:
                self.comboBox_product_type_edit.setCurrentText(product[2])
                self.lineEdit_6.setText(product[3])
                self.lineEdit_8.setText(product[4])
                # Convert string date to QDate
                date = QDate.fromString(product[5], "yyyy-MM-dd")
                self.dateEdit_production_edit.setDate(date)
                
            print(f"Switching to EDIT page. Current index: {self.stackedWidget_2.currentIndex()}")
        except Exception as e:
            print(f"Error in show_edit_page: {e}")
            QMessageBox.warning(self, "Error", f"Failed to switch to EDIT page: {e}")

    def save_edit_product(self):
        """Save edited product to database"""
        try:
            current_item = self.listWidget.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Warning", "Vui lòng chọn sản phẩm cần sửa!")
                return

            product_code = current_item.text().split("|")[0].split(":")[1].strip()
            product_type = self.comboBox_product_type_edit.currentText()
            product_name = self.lineEdit_6.text().strip()
            manufacturer = self.lineEdit_8.text().strip()
            production_date = self.dateEdit_production_edit.date().toString("yyyy-MM-dd")

            # Validate all fields
            if not product_name:
                QMessageBox.warning(self, "Warning", "Vui lòng nhập tên sản phẩm!")
                self.lineEdit_6.setFocus()
                return
            if not manufacturer:
                QMessageBox.warning(self, "Warning", "Vui lòng nhập nhà sản xuất!")
                self.lineEdit_8.setFocus()
                return

            conn = sqlite3.connect("techshop.db")
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET product_type = ?, product_name = ?, manufacturer = ?, production_date = ?
                WHERE product_code = ?
            ''', (product_type, product_name, manufacturer, production_date, product_code))
            conn.commit()
            QMessageBox.information(self, "Success", "Cập nhật sản phẩm thành công!")
            self.load_products()
            self.slide_to_page(4)  # Switch back to CRUD page
        except Exception as e:
            print(f"Error in save_edit_product: {e}")
            QMessageBox.warning(self, "Error", f"Lỗi khi cập nhật sản phẩm: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_product(self):
        """Delete selected product from database"""
        current_item = self.listWidget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a product to delete!")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            product_code = current_item.text().split("|")[0].split(":")[1].strip()
            try:
                conn = sqlite3.connect("techshop.db")
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products WHERE product_code = ?', (product_code,))
                conn.commit()
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products()
            except:
                QMessageBox.warning(self, "Error", "Failed to delete product!")
            finally:
                conn.close()

    def setup_product_type_comboboxes(self):
        """Setup product type comboboxes for both add and edit pages"""
        # Add page
        self.comboBox_product_type = QComboBox(self)
        self.comboBox_product_type.addItems(self.product_types)
        self.comboBox_product_type.setStyleSheet("""
            QComboBox {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #ebdfc0;
                border-radius: 15px;
            }
        """)
        # Replace lineEdit with combobox in the layout
        if hasattr(self, 'lineEdit'):
            self.verticalLayout_17.replaceWidget(self.lineEdit, self.comboBox_product_type)
            self.lineEdit.hide()  # Hide instead of delete
        
        # Edit page
        self.comboBox_product_type_edit = QComboBox(self)
        self.comboBox_product_type_edit.addItems(self.product_types)
        self.comboBox_product_type_edit.setStyleSheet("""
            QComboBox {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #555555;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #ebdfc0;
                border-radius: 15px;
            }
        """)
        # Replace lineEdit_5 with combobox in the layout
        if hasattr(self, 'lineEdit_5'):
            self.verticalLayout_21.replaceWidget(self.lineEdit_5, self.comboBox_product_type_edit)
            self.lineEdit_5.hide()  # Hide instead of delete

    def setup_date_pickers(self):
        """Setup date pickers for both add and edit pages"""
        # Add page
        self.dateEdit_production = QDateEdit(self)
        self.dateEdit_production.setCalendarPopup(True)
        self.dateEdit_production.setDate(QDate.currentDate())
        self.dateEdit_production.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #555555;
                padding: 5px;
            }
            QDateEdit:hover {
                background-color: #ebdfc0;
                border-radius: 15px;
            }
        """)
        # Replace lineEdit_4 with dateEdit in the layout
        if hasattr(self, 'lineEdit_4'):
            self.verticalLayout_18.replaceWidget(self.lineEdit_4, self.dateEdit_production)
            self.lineEdit_4.hide()  # Hide instead of delete
        
        # Edit page
        self.dateEdit_production_edit = QDateEdit(self)
        self.dateEdit_production_edit.setCalendarPopup(True)
        self.dateEdit_production_edit.setDate(QDate.currentDate())
        self.dateEdit_production_edit.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #555555;
                padding: 5px;
            }
            QDateEdit:hover {
                background-color: #ebdfc0;
                border-radius: 15px;
            }
        """)
        # Replace lineEdit_7 with dateEdit in the layout
        if hasattr(self, 'lineEdit_7'):
            self.verticalLayout_22.replaceWidget(self.lineEdit_7, self.dateEdit_production_edit)
            self.lineEdit_7.hide()  # Hide instead of delete

    def show_add_page(self):
        """Switch to add product page"""
        try:
            # Clear all input fields first
            self.lineEdit_2.clear()
            self.lineEdit_3.clear()
            
            # Reset combobox and date picker
            self.comboBox_product_type.setCurrentIndex(0)
            self.dateEdit_production.setDate(QDate.currentDate())
            
            # Switch to ADD page
            self.slide_to_page(5)  # Changed from 4 to 5 for ADD page
            
            # Debug message
            print(f"Switching to ADD page. Current index: {self.stackedWidget_2.currentIndex()}")
        except Exception as e:
            print(f"Error in show_add_page: {e}")
            QMessageBox.warning(self, "Error", f"Failed to switch to ADD page: {e}")

    def save_new_product(self):
        """Save a new product to database"""
        try:
            # Get values from input fields
            product_type = self.comboBox_product_type.currentText()
            product_name = self.lineEdit_2.text().strip()
            manufacturer = self.lineEdit_3.text().strip()
            production_date = self.dateEdit_production.date().toString("yyyy-MM-dd")

            # Generate product code
            product_code = f"SP{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Validate all fields
            if not product_name:
                QMessageBox.warning(self, "Warning", "Vui lòng nhập tên sản phẩm!")
                self.lineEdit_2.setFocus()
                return
            if not manufacturer:
                QMessageBox.warning(self, "Warning", "Vui lòng nhập nhà sản xuất!")
                self.lineEdit_3.setFocus()
                return

            conn = sqlite3.connect("techshop.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (product_code, product_type, product_name, manufacturer, production_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_code, product_type, product_name, manufacturer, production_date))
            conn.commit()
            QMessageBox.information(self, "Success", "Thêm sản phẩm thành công!")
            self.load_products()
            self.slide_to_page(4)  # Switch back to CRUD page
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Lỗi khi thêm sản phẩm!")
        except Exception as e:
            print(f"Error in save_new_product: {e}")
            QMessageBox.warning(self, "Error", f"Lỗi khi thêm sản phẩm: {e}")
        finally:
            if 'conn' in locals():
                conn.close()


           





