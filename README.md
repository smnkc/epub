# PDF ve Word → EPUB Dönüştürücü

PDF ve Word dosyalarını EPUB formatına dönüştüren kullanıcı dostu bir uygulama.

## Özellikler

- PDF dosyalarını EPUB formatına dönüştürme
- Word (.docx, .doc) dosyalarını EPUB formatına dönüştürme
- Sürükle-bırak dosya yükleme
- Toplu dosya dönüştürme
- Özel çıktı klasörü seçimi
- Kullanıcı dostu arayüz

## Kurulum

1. Python 3.7 veya daha yeni bir sürümü yüklü olmalıdır.
2. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

## Kullanım

Uygulamayı başlatmak için:

```bash
python app.py
```

### Dönüştürücü

#### PDF veya Word Dosyasını EPUB'a Dönüştürme

1. "Dönüştürücü" sekmesine geçin
2. "Dosya Ekle" butonuna tıklayın veya dosyaları uygulama penceresine sürükleyip bırakın
3. Dönüştürmek istediğiniz PDF veya Word dosyasını seçin
4. İsteğe bağlı olarak "Gözat" butonu ile çıktı klasörünü değiştirin
5. "Dönüştür" butonuna tıklayın
6. Dönüştürme tamamlandığında, EPUB dosyası seçilen klasörde oluşturulacaktır

## Dönüştürme Özellikleri

### PDF → EPUB
- PDF metinlerini ayıklama ve yapılandırma
- Sayfa düzenini koruma
- Okuyucu dostu EPUB formatına dönüştürme

### Word → EPUB
- Metinleri, başlıkları ve paragrafları koruma
- Belgedeki resimleri EPUB formatına dahil etme
- Stillendirilmiş içeriği HTML formatına dönüştürme

## Gereksinimler

Aşağıdaki Python kütüphaneleri gereklidir:

- PyQt5 (GUI arayüzü için)
- PyPDF2 (PDF dosyalarını işlemek için)
- python-docx (Word dosyalarını işlemek için)
- ebooklib (EPUB formatını oluşturmak ve okumak için)
- Pillow (Resimleri işlemek için)
- beautifulsoup4 ve lxml (HTML içeriğini işlemek için)

Bu kütüphaneler `requirements.txt` dosyasında belirtilmiştir.
