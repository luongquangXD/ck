import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtGui import QIcon
# Kiểm tra xem thư viện google-generativeai đã được cài đặt chưa
try:
    import google.generativeai as genai
except ImportError:
    print("Thư viện 'google-generativeai' chưa được cài đặt.")
    print("Vui lòng cài đặt bằng lệnh: pip install google-generativeai")
    sys.exit()

# Thay thế YOUR_API_KEY bằng API key thực tế của bạn
API_KEY = "AIzaSyCZV_C-_5Y94x-lmyg5nL5H6EsOTFC7L_8"
if not API_KEY:
    print("Bạn chưa thiết lập biến môi trường GOOGLE_API_KEY.")
    print("Vui lòng thiết lập biến môi trường này với API key Gemini của bạn.")
    sys.exit()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

class GeminiThread(QThread):
    response_received = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            response = model.generate_content(self.prompt)
            self.response_received.emit(response.text)
        except Exception as e:
            self.response_received.emit(f"Lỗi: {e}")

class ChatDisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.icon = QIcon("./picture/gemini.png")
        self.setWindowTitle("ChatBotGemini_flash_2.0")
        self.setWindowIcon(self.icon)
        self.setGeometry(100, 100, 400, 400)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_display)
        self.setLayout(main_layout)

    def display_message(self, message):
        self.chat_display.append(message)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

class InputControlWindow(QWidget):
    send_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.icon = QIcon("./picture/gemini.png")
        self.setWindowTitle("Nhập câu hỏi để trò chuyên với Gemini")
        self.setWindowIcon(self.icon)
        self.setGeometry(520, 100, 300, 100)

        self.user_input = QLineEdit()
        self.send_button = QPushButton("Gửi")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

        self.send_button.clicked.connect(self.send_message)
        self.user_input.returnPressed.connect(self.send_message)

    def send_message(self):
        user_text = self.user_input.text().strip()
        if user_text:
            self.send_requested.emit(user_text)
            self.user_input.clear()

class GeminiChatbot:
    def __init__(self):
        self.chat_window = ChatDisplayWindow()
        self.input_window = InputControlWindow()

        masked_key = f"{'*' * (len(API_KEY) - 5)}{API_KEY[-5:]}"
        api_key_label = QLabel(f"API Key đang dùng: {masked_key}")
        api_key_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout = QVBoxLayout(self.input_window)
        layout.addWidget(api_key_label)
        self.input_window.setLayout(layout)

        self.input_window.send_requested.connect(self.send_message)

    def show(self):
        self.chat_window.show()
        self.input_window.show()

    def send_message(self, user_text):
        self.chat_window.display_message(f"Bạn 👨‍💻ο(=•ω＜=)ρ⌒☆: {user_text}")
        self.start_gemini_thread(user_text)

    def start_gemini_thread(self, prompt):
        self.gemini_thread = GeminiThread(prompt)
        self.gemini_thread.response_received.connect(self.display_gemini_response)
        self.gemini_thread.start()
        self.input_window.send_button.setEnabled(False)
        self.input_window.user_input.setEnabled(False)
        self.chat_window.display_message("Gemini đang trả lời ☆* .｡. o(≧▽≦)o .｡.:*☆")

    def display_gemini_response(self, response_text):
        self.chat_window.display_message(f"Gemini (*>﹏<*)💻: {response_text}")
        self.input_window.send_button.setEnabled(True)
        self.input_window.user_input.setEnabled(True)
        self.input_window.user_input.setFocus()
    