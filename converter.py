import os
import tempfile
from pathlib import Path
import uuid

import PyPDF2
import docx
from ebooklib import epub
from PIL import Image
import io
from bs4 import BeautifulSoup
import re

class Converter:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def pdf_to_epub(self, pdf_path, output_path=None):
        """PDF dosyasını EPUB formatına dönüştürür"""
        if output_path is None:
            output_path = str(Path(pdf_path).with_suffix('.epub'))
            
        # EPUB kitap oluştur
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(Path(pdf_path).stem)
        book.set_language('tr')
        
        # PDF'i aç ve içeriğini oku
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            chapters = []
            spine = ['nav']
            
            # Her sayfayı bir bölüm olarak ekle
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # HTML içeriği oluştur
                    chapter_title = f"Sayfa {i+1}"
                    chapter_filename = f"page_{i+1}.xhtml"
                    
                    # Metni paragrafları böl ve HTML formatına dönüştür
                    paragraphs = text.split('\n\n')
                    html_content = "<h1>" + chapter_title + "</h1>"
                    for para in paragraphs:
                        if para.strip():
                            html_content += f"<p>{para}</p>"
                    
                    # Bölümü oluştur
                    chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_filename)
                    chapter.content = f'<html><body>{html_content}</body></html>'
                    
                    # Kitaba ekle
                    book.add_item(chapter)
                    chapters.append(chapter)
                    spine.append(chapter)
            
            # İçindekiler tablosu oluştur
            book.toc = chapters
            book.spine = spine
            
            # CSS stili ekle
            style = """
            body {
                font-family: Times New Roman, Times, serif;
                margin: 5%;
                text-align: justify;
            }
            h1 {
                text-align: center;
                font-size: 1.5em;
                margin-bottom: 1em;
            }
            p {
                text-indent: 1em;
                margin-top: 0.5em;
                margin-bottom: 0.5em;
            }
            """
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(nav_css)
            
            # Navigasyon dosyası ekle
            nav = epub.EpubNav()
            book.add_item(nav)
            
            # EPUB dosyasını yaz
            epub.write_epub(output_path, book)
            
            return output_path
    
    def docx_to_epub(self, docx_path, output_path=None):
        """DOCX dosyasını EPUB formatına dönüştürür"""
        if output_path is None:
            output_path = str(Path(docx_path).with_suffix('.epub'))
            
        # EPUB kitap oluştur
        book = epub.EpubBook()
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(Path(docx_path).stem)
        book.set_language('tr')
        
        # Word dosyasını aç
        doc = docx.Document(docx_path)
        
        # Ana içerik
        content = ""
        for para in doc.paragraphs:
            if para.text.strip():
                style = para.style.name
                
                # Başlıklar için
                if 'Heading' in style:
                    level = int(style.replace('Heading ', '')) if style != 'Heading' else 1
                    content += f"<h{level}>{para.text}</h{level}>"
                else:
                    # Paragraf stillerini HTML'e dönüştür
                    html_para = f"<p>{para.text}</p>"
                    content += html_para
        
        # Resimler için
        image_count = 0
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_count += 1
                    image_data = rel.target_part.blob
                    img = Image.open(io.BytesIO(image_data))
                    
                    # Resmi geçici dosyaya kaydet
                    img_path = os.path.join(self.temp_dir, f"image_{image_count}.png")
                    img.save(img_path)
                    
                    # EPUB'a ekle
                    img_item = epub.EpubItem(
                        uid=f"image_{image_count}",
                        file_name=f"images/image_{image_count}.png",
                        media_type="image/png",
                        content=open(img_path, 'rb').read()
                    )
                    book.add_item(img_item)
                    
                    # İçeriğe resim ekle
                    content += f'<div class="image-container"><img src="images/image_{image_count}.png" alt="Resim {image_count}"/></div>'
                except Exception as e:
                    print(f"Resim dönüştürme hatası: {e}")
        
        # Ana bölüm oluştur
        chapter = epub.EpubHtml(title="İçerik", file_name="content.xhtml")
        chapter.content = f'<html><body>{content}</body></html>'
        book.add_item(chapter)
        
        # CSS stili ekle
        style = """
        body {
            font-family: Times New Roman, Times, serif;
            margin: 5%;
            text-align: justify;
        }
        h1 {
            text-align: center;
            font-size: 1.8em;
            margin-bottom: 1em;
        }
        h2 {
            font-size: 1.5em;
            margin-top: 1em;
        }
        h3 {
            font-size: 1.3em;
        }
        p {
            text-indent: 1em;
            margin-top: 0.5em;
            margin-bottom: 0.5em;
        }
        .image-container {
            text-align: center;
            margin: 1em 0;
        }
        img {
            max-width: 90%;
            height: auto;
        }
        """
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)
        
        # İçindekiler ve kitap yapısı
        book.toc = [chapter]
        book.spine = ['nav', chapter]
        
        # Navigasyon dosyası ekle
        nav = epub.EpubNav()
        book.add_item(nav)
        
        # EPUB dosyasını yaz
        epub.write_epub(output_path, book)
        
        return output_path
        
    def clean_up(self):
        """Geçici dosyaları temizle"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass 