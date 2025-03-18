import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QFileDialog, QComboBox, QMessageBox,
    QProgressBar, QFrame, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent

from converter import Converter

class ConversionThread(QThread):
    """Dönüştürme işlemini arka planda gerçekleştiren iş parçacığı"""
    progress_update = pyqtSignal(str)
    conversion_finished = pyqtSignal(str)
    conversion_error = pyqtSignal(str)
    
    def __init__(self, file_path, output_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.output_path = output_path
        self.converter = Converter()
    
    def run(self):
        try:
            file_ext = Path(self.file_path).suffix.lower()
            self.progress_update.emit("Dönüştürme başlatılıyor...")
            
            if file_ext == '.pdf':
                self.progress_update.emit("PDF içeriği okunuyor...")
                output = self.converter.pdf_to_epub(self.file_path, self.output_path)
                
            elif file_ext in ['.docx', '.doc']:
                self.progress_update.emit("Word içeriği okunuyor...")
                output = self.converter.docx_to_epub(self.file_path, self.output_path)
                
            else:
                self.conversion_error.emit(f"Desteklenmeyen dosya formatı: {file_ext}")
                return
                
            self.progress_update.emit("EPUB dosyası oluşturuluyor...")
            self.progress_update.emit("Dönüştürme tamamlandı!")
            self.conversion_finished.emit(output)
            
        except Exception as e:
            self.conversion_error.emit(f"Dönüştürme hatası: {str(e)}")
        finally:
            # Geçici dosyaları temizle
            self.converter.clean_up()


class ConverterWidget(QWidget):
    """Dönüştürücü penceresi"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.files_to_convert = []
        self.setAcceptDrops(True)
        
    def init_ui(self):
        # Ana layout
        main_layout = QVBoxLayout()
        
        # Başlık
        title_label = QLabel("PDF ve Word Dosyalarını EPUB Formatına Dönüştürün")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Kullanım talimatları
        info_label = QLabel("Dönüştürmek istediğiniz dosyaları sürükleyip bırakın veya 'Dosya Ekle' butonuna tıklayın")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Dosya listesi
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        main_layout.addWidget(self.file_list)
        
        # Butonlar için yatay düzen
        buttons_layout = QHBoxLayout()
        
        # Dosya ekleme butonu
        self.add_file_btn = QPushButton("Dosya Ekle")
        self.add_file_btn.setMinimumHeight(40)
        self.add_file_btn.clicked.connect(self.add_files)
        buttons_layout.addWidget(self.add_file_btn)
        
        # Listeyi temizleme butonu
        self.clear_list_btn = QPushButton("Listeyi Temizle")
        self.clear_list_btn.setMinimumHeight(40)
        self.clear_list_btn.clicked.connect(self.clear_file_list)
        buttons_layout.addWidget(self.clear_list_btn)
        
        main_layout.addLayout(buttons_layout)
        
        # Çıktı klasörü seçimi
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Çıktı Klasörü:"))
        
        self.output_dir_label = QLabel("Aynı klasör")
        output_layout.addWidget(self.output_dir_label)
        
        self.browse_output_btn = QPushButton("Gözat")
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_output_btn)
        
        main_layout.addLayout(output_layout)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Dönüştürme butonu
        self.convert_btn = QPushButton("Dönüştür")
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.clicked.connect(self.start_conversion)
        main_layout.addWidget(self.convert_btn)
        
        # İlerleme çubuğu
        self.progress_label = QLabel("Hazır")
        self.progress_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.progress_label)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Çıktı klasörü
        self.output_dir = None
        
        # Widget'ı ayarla
        self.setLayout(main_layout)
        
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Dönüştürülecek Dosyaları Seçin",
            "",
            "Desteklenen Dosyalar (*.pdf *.docx *.doc)"
        )
        
        if files:
            for file_path in files:
                self.add_file_to_list(file_path)
    
    def add_file_to_list(self, file_path):
        # Dosya zaten listede var mı kontrol et
        for i in range(self.file_list.count()):
            if self.file_list.item(i).data(Qt.UserRole) == file_path:
                return
                
        # Dosya adını ve tam yolu ekle
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.UserRole, file_path)
        self.file_list.addItem(item)
    
    def clear_file_list(self):
        self.file_list.clear()
    
    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "Çıktı Klasörünü Seçin",
            ""
        )
        
        if dir_path:
            self.output_dir = dir_path
            # Yolu kısaltarak göster
            path = Path(dir_path)
            if len(str(path)) > 30:
                self.output_dir_label.setText(f"...{str(path)[-30:]}")
            else:
                self.output_dir_label.setText(str(path))
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        # Sadece dosya sürüklemelerini kabul et
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        # Bırakılan dosyaları al
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            ext = Path(file_path).suffix.lower()
            
            # Sadece PDF ve Word dosyalarını kabul et
            if ext in ['.pdf', '.docx', '.doc']:
                self.add_file_to_list(file_path)
    
    def start_conversion(self):
        # Dönüştürülecek dosya var mı kontrol et
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce dönüştürülecek dosya ekleyin.")
            return
        
        # Tüm dosyalar için dönüştürme işlemi başlat
        self.completed_count = 0
        self.total_count = self.file_list.count()
        self.progress_bar.setRange(0, self.total_count)
        self.progress_bar.setValue(0)
        
        # İlk dosyayı dönüştür
        self.convert_next_file()
    
    def convert_next_file(self):
        # Tüm dosyalar dönüştürüldü mü kontrol et
        if self.completed_count >= self.total_count:
            self.progress_label.setText("Tüm dönüştürmeler tamamlandı!")
            QMessageBox.information(self, "Başarılı", "Tüm dosyalar başarıyla dönüştürüldü.")
            return
        
        # Sıradaki dosyayı al ve dönüştür
        item = self.file_list.item(self.completed_count)
        file_path = item.data(Qt.UserRole)
        file_name = Path(file_path).name
        
        self.progress_label.setText(f"Dönüştürülüyor: {file_name}")
        
        # Çıktı dosyası yolunu belirle
        output_path = None
        if self.output_dir:
            output_filename = Path(file_path).stem + ".epub"
            output_path = os.path.join(self.output_dir, output_filename)
        
        # Dönüştürme işlemini başlat
        self.thread = ConversionThread(file_path, output_path)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.conversion_finished.connect(self.on_conversion_success)
        self.thread.conversion_error.connect(self.on_conversion_error)
        self.thread.start()
    
    def update_progress(self, message):
        self.progress_label.setText(message)
    
    def on_conversion_success(self, output_path):
        # İlerleme bilgisini güncelle
        self.completed_count += 1
        self.progress_bar.setValue(self.completed_count)
        
        # Başarılı dönüştürme işaretini ekle
        item = self.file_list.item(self.completed_count - 1)
        item.setText(f"✓ {item.text()} → {Path(output_path).name}")
        
        # Sıradaki dosyayı dönüştür
        self.convert_next_file()
    
    def on_conversion_error(self, error_message):
        # Hata işareti ekle
        item = self.file_list.item(self.completed_count)
        item.setText(f"✗ {item.text()} - HATA")
        
        self.completed_count += 1
        self.progress_bar.setValue(self.completed_count)
        
        # Hata mesajını göster
        self.progress_label.setText(f"Hata: {error_message}")
        
        # Sıradaki dosyayı dönüştür
        self.convert_next_file()





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("PDF ve Word → EPUB Dönüştürücü")
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana düzen
        main_layout = QVBoxLayout(central_widget)
        
        # Dönüştürücü widget'ı
        self.converter_widget = ConverterWidget()
        main_layout.addWidget(self.converter_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())