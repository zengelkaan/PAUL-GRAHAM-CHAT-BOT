#  WEB SCRAPING: PAUL GRAHAM MAKALALERİNİ ÇEKME, TEK SEFERLİK ÇALIŞIR, EMBEDDİNG OLUŞTURMAZ
#paul-graham-agent/articles.py oluşturur

import requests # Requests = HTTP istekleri yapmak için, web sayfalarını çekmek için, GET gibi
from bs4 import BeautifulSoup #HTML sayfalarını ayrıştırmak için, web sayfalarını parse etmek için, HTML içeriğini okumak için
#html sayfalarını doğrudan okumak zor olduğu için, BeautifulSoup kullanılır, HTML etiketlerini kolayca ayıklamak için
import os # OS = Dosya ve klasör işlemleri için, makaleleri kaydetmek için klasör oluşturmak, dosyaları yazmak için
import time # Siteye art arda istek atıyoruz, bot sanılabilir, bekleme süreleri eklemek için

base_url = "http://paulgraham.com/" # Paul Graham'ın makalelerinin bulunduğu ana URL
index_url = base_url + "articles.html" # Makalelerin listelendiği sayfanın URL'si

os.makedirs("paul_graham_articles", exist_ok=True) # Klasör var mı kontrol et, yoksa oluştur, exist_ok=True = zaten varsa hata verme

# 2. Ana sayfadan makale linklerini çek
response = requests.get(index_url) # GET isteği ile makalelerin listelendiği sayfayı çek, response.text = HTML içeriği
soup = BeautifulSoup(response.text, "html.parser") # BeautifulSoup ile HTML içeriğini ayrıştır, "html.parser" = HTML ayrıştırıcı kullan
links = soup.find_all("a") # "a" link demek, tüm linkleri bul

for link in links:
    href = link.get("href") #linkin url'sini al, "href" = linkin adresi, "essays.html" gibi
    if href and href.endswith(".html") and not href.startswith("http"): # href boş değilse, ".html" ile bitiyorsa ve "http" ile başlamıyorsa
        full_url = base_url + href # Tam URL'yi oluştur, base_url + href = http://paulgraham.com/essays.html gibi
        try: 
            article = requests.get(full_url) # Tam URL'ye GET isteği at, makalenin içeriğini çek, indir
            article_soup = BeautifulSoup(article.text, "html.parser") # HTML içeriğini ayrıştır, makalenin içeriğini BeautifulSoup ile ayrıştır
            text = article_soup.get_text(separator="\n")  # Metni sadece yazı olarak al, etkiketleri kaldır, get_text() = HTML etiketlerini kaldırır, sadece metni alır, separator="\n" = satırları ayırmak için yeni satır karakteri kullan

            filename = href.replace(".html", "") + ".txt" # Dosya adını oluştur, ".html" uzantısını kaldır ve ".txt" ile değiştir, örneğin "essays" → "essays.txt"
            filepath = os.path.join("paul_graham_articles", filename) # Dosya yolunu oluştur, "paul_graham_articles" klasöründe dosya adını ekle, tam yol: "paul_graham_articles/essays.txt"

            with open(filepath, "w", encoding="utf-8") as f: # Dosyayı yazma modunda aç, "w" = yazma modu, encoding="utf-8" = Türkçe karakterleri düzgün yazmak için
                f.write(text)

            print(f"Saved: {filename}") # Başarılı bir şekilde kaydedildi mesajı yazdır, hangi dosyanın kaydedildiğini gösterir
            time.sleep(1)  # Siteyi yormamak için bekle, bot sanılmamak için 1 saniye bekle

        except Exception as e:  # hata yakala, e = hata mesajı
            print(f"Failed to fetch {full_url} → {e}")

# Eğer try bloğu içinde bir hata oluşursa, except bloğu çalışır ve hata mesajını yazdırır. Bu sayede program durmaz ve diğer makaleleri çekmeye devam eder.
