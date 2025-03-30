from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QProgressBar
)
from PyQt6.QtCore import pyqtSlot, QTimer, Qt
from PyQt6.QtGui import QMovie, QPainter, QPixmap

import sys
import psutil
import gpustat
import threading
import subprocess
from playsound import playsound

import llm_utils as llmu
from ASR_modules import asr_helper
from TTS_modules import tts_helper

statusToColor = {
    "Deactivated": "salmon",
    "Loading ASR engine...": "lightyellow",
    "Loading TTS engine...": "lightyellow",
    "Listening...": "mediumturquoise",
    "Please say your command...": "mintcream",
    "Thinking...": "lightskyblue",
    "Responding...": "aquamarine"
}
statusToGif = {
    "Deactivated": "",
    "Loading ASR engine...": "res/3.gif",
    "Loading TTS engine...": "res/3.gif",
    "Listening...": "res/4.gif",
    "Please say your command...": "res/4.gif",
    "Thinking...": "res/4.gif",
    "Responding...": "res/4.gif"
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()

        self.lang = 'en'
        self.keyword = 'hello'
        self.assistant_loaded = False
        self.selected_model = ""
        self.status = ""
        self.assitant_thread = None

        self.movie = QMovie()
        
        # Initialize UI elements
        self.setWindowTitle("Voice AI assistant")
        self.setGeometry(500, 500, 800, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Russian"])
        self.lang_combo.currentTextChanged.connect(self.on_language_change)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        
        # Model selector
        model_layout = QHBoxLayout()
        model_label = QLabel("LLM model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(llmu.get_model_list())  # Add your models here
        self.selected_model = self.model_combo.currentText()
        self.model_combo.currentTextChanged.connect(self.on_model_change)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)

        asr_layout = QHBoxLayout()
        asr_layout.addWidget(QLabel("ASR module:"))
        self.asr_combo = QComboBox()
        self.asr_combo.addItems(asr_helper.get_available_asr())
        self.current_asr = self.asr_combo.currentText()
        self.asr_combo.currentTextChanged.connect(self.on_asr_change)
        asr_layout.addWidget(self.asr_combo)
        
        tts_layout = QHBoxLayout()
        tts_layout.addWidget(QLabel("TTS module:"))
        self.tts_combo = QComboBox()
        self.tts_combo.addItems(tts_helper.get_available_tts())
        self.current_tts = self.tts_combo.currentText()
        self.tts_combo.currentTextChanged.connect(self.on_tts_change)
        tts_layout.addWidget(self.tts_combo)

        # Keyword input
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel("Keyword:")
        self.keyword_input = QLineEdit(self.keyword)
        self.keyword_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keyword_input.textChanged.connect(self.on_keyword_change)
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)

        llmGroupBox = QGroupBox("Assitant settings:")
        llmGroupBoxLayout = QVBoxLayout()
        llmGroupBoxLayout.addLayout(model_layout)
        llmGroupBoxLayout.addLayout(keyword_layout)
        llmGroupBox.setLayout(llmGroupBoxLayout)

        # Status display
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Status: deactivated")
        status_layout.addStretch(10)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch(10)

        self.activate_button = QPushButton("Activate")
        self.activate_button.setCheckable(True)
        self.activate_button.clicked.connect(self.startAssistant)

        self.cpu_label = QProgressBar()
        self.gpu_label = QProgressBar()
        self.ram_label = QProgressBar()
        self.vram_label = QProgressBar()
        
        stat_layout = QHBoxLayout()
        stat_layout.addWidget(self.cpu_label)
        stat_layout.addWidget(self.gpu_label)
        stat_layout2 = QHBoxLayout()
        stat_layout2.addWidget(self.ram_label)
        stat_layout2.addWidget(self.vram_label)
        
        # Add layouts to main layout
        main_layout.addLayout(lang_layout)
        main_layout.addLayout(asr_layout)
        main_layout.addLayout(tts_layout)
        main_layout.addWidget(llmGroupBox)
        main_layout.addStretch(10)
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.activate_button)
        main_layout.addStretch(10)
        main_layout.addLayout(stat_layout)
        main_layout.addLayout(stat_layout2)

        # Set central widget
        self.setCentralWidget(central_widget)

        # Initialize timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second
        
        # First update
        self.update_metrics()
        self.set_status_text('Deactivated')
    
    def paintEvent(self, event):
        current_frame = self.movie.currentPixmap()
        frame_rect = current_frame.rect()
        frame_rect.moveCenter(self.rect().center())
        
        if frame_rect.intersects(event.rect()):
            painter = QPainter(self)
            painter.drawPixmap(frame_rect.left(), frame_rect.top(), current_frame)

    def closeEvent(self, event):
        self.stop_model(self.selected_model)
        event.accept()

    @pyqtSlot(str)
    def on_model_change(self, text):
        self.set_status_text(f"Stopping {self.selected_model} model...")
        self.stop_model(self.selected_model)
        self.selected_model = text  # Store the selected model  
        self.set_status_text(f"Loading {self.selected_model} model...")
        self.start_model(self.selected_model)
        self.set_status_text(f"Model {self.selected_model} loaded!")

    def start_model(self, name):
        try:
            result = subprocess.run(
                ["ollama", "run", name],
                capture_output=True,
                text=True,
                check=True
            )
            print("Ollama is running")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e.stderr}")
            return False
        except FileNotFoundError:
            print("Error: Ollama is not installed or not in PATH")
            return False
    
    def stop_model(self, name):
        try:
            subprocess.run(["ollama", "stop", name], check=True)
            print(f"Stopped model: {name}")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping model: {e}")

    @pyqtSlot(str)
    def on_language_change(self, text):
        self.set_status_text(f"Language changed to: {text}")
        self.lang = 'en' if text == 'English' else 'ru'
        self.keyword_input.setText('hello' if self.lang == 'en' else 'привет')
        self.keyword = self.keyword_input.text()
        
    @pyqtSlot(str)
    def on_keyword_change(self, text):
        self.keyword = text
        self.set_status_text(f"Keyword updated: {text}")
        
    def set_status_text(self, text):
        if self.status == text:
            return
        self.status = text
        self.status_label.setText(f"Status: {text}")

    @pyqtSlot(str)
    def on_asr_change(self, text):
        self.current_asr = text

    @pyqtSlot(str)
    def on_tts_change(self, text):
        self.current_tts = text

    @pyqtSlot(bool)
    def startAssistant(self, clicked):
        self.running = clicked
        if clicked:
            self.stop_event.clear()
            self.lang_combo.setEnabled(False)
            self.asr_combo.setEnabled(False)
            self.tts_combo.setEnabled(False)
            self.model_combo.setEnabled(False)
            self.activate_button.setText("Deactivate")
            self.start_model(self.selected_model)
            if not self.assistant_loaded:
                self.assitant_thread = threading.Thread(target=self.run_assitant)
                self.assitant_thread.daemon = True  # Thread dies when main app closes
                self.assitant_thread.start()
                self.assistant_loaded = True
        else:
            self.stop_model(self.selected_model)
            if self.assitant_thread is not None:
                self.stop_event.set()
                #time.sleep(1)
                #self.assitant_thread.join()
                self.assitant_thread = None
                self.assistant_loaded = False
            self.set_status_text("Deactivated")
            self.activate_button.setText("Activate")
            self.lang_combo.setEnabled(True)
            self.asr_combo.setEnabled(True)
            self.tts_combo.setEnabled(True)
            self.model_combo.setEnabled(True)
        
    def run_assitant(self):
        self.set_status_text("Loading TTS engine...")
        engine = tts_helper.get_voice_engine(self.current_tts, self.lang)
        self.set_status_text("Loading ASR engine...")
        asr_engine = asr_helper.get_asr_engine(self.current_asr, self.lang)
        while not self.stop_event.is_set():
            self.set_status_text(f"Listening for \"{self.keyword}\" keyword...")
            if asr_helper.detect_keyword(self.current_asr, self.keyword, asr_engine, lambda: self.stop_event.is_set()):
                if self.stop_event.is_set():
                    break
                playsound('res/mixkit-select-click-1109.wav')
                self.set_status_text("Listening for your command...")
                command = asr_helper.capture_command(self.current_asr, asr_engine, lambda: self.stop_event.is_set())
                while not self.stop_event.is_set() and command:
                    self.set_status_text("Thinking...")
                    response = llmu.get_response(command, self.selected_model, self.lang)
                    thoughts, response = llmu.parse_response(response.message.content)
                    llmu.print_model_response(thoughts, response)
                    self.set_status_text("Responding...")
                    tts_helper.text_to_speech(self.current_tts, engine, '\n'.join(response), self.lang, lambda: self.stop_event.is_set())
                    self.set_status_text("Please say your command...")
                    command = asr_helper.capture_command(self.current_asr, asr_engine, lambda: self.stop_event.is_set())
                self.set_status_text("Listening for the keyword...")
            else:
                playsound('res/mixkit-click-error-1110.wav')
        print('Finished assistant thread!')
    
    def format_size(self, bytes, units):
        """Convert bytes to human readable format."""
        for unit in units:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} UU"

    def update_metrics(self):
        if self.status in statusToGif.keys():
            if self.movie.fileName() != statusToGif[self.status]:
                self.movie = QMovie(statusToGif[self.status])
                if statusToGif[self.status]:
                    self.movie.frameChanged.connect(self.repaint)
                    self.movie.start()
            
        #if self.status in statusToColor.keys():
            #self.setStyleSheet("QMainWindow { background-color: " + statusToColor[self.status] + "; }")
        # Get CPU usage
        cpu_percent = psutil.cpu_percent()
        self.cpu_label.setFormat(f"CPU: %p%")
        self.cpu_label.setMinimum(0)
        self.cpu_label.setMaximum(100)
        self.cpu_label.setValue(int(cpu_percent))

        # Get RAM usage
        ram = psutil.virtual_memory()
        ram_used = self.format_size(ram.used, ['B', 'KB', 'MB', 'GB'])
        ram_total = self.format_size(ram.total, ['B', 'KB', 'MB', 'GB'])
        self.ram_label.setMinimum(0)
        self.ram_label.setMaximum(int(ram.total/1024/1024))
        self.ram_label.setValue(int(ram.used/1024/1024))
        self.ram_label.setFormat(f"RAM: %p% ({ram_used}/{ram_total})")
        
        # Get GPU usage (only if NVIDIA GPU present)
        try:
            gpu_stats = gpustat.GPUStatCollection.new_query()
            if gpu_stats.gpus:
                self.gpu_label.setMinimum(0)
                self.gpu_label.setMaximum(100)
                self.gpu_label.setValue(gpu_stats.gpus[0].utilization)
                self.gpu_label.setFormat('GPU: %p%')

                mem_used = gpu_stats.gpus[0].memory_used
                mem_total = gpu_stats.gpus[0].memory_total
                self.vram_label.setMinimum(0)
                self.vram_label.setMaximum(mem_total)
                self.vram_label.setValue(mem_used)
                self.vram_label.setFormat(f'VRAM: %p% ({self.format_size(mem_used, ['MB', 'GB'])}/{self.format_size(mem_total, ['MB', 'GB'])})')
            else:
                self.gpu_label.setText("GPU: Not detected")
                self.vram_label.setText("VRAM: Not detected")
        except Exception as e:
            print(f"Error GPU ({str(e)})")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


