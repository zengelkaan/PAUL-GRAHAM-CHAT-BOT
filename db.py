# RAG (Retrieval-Augmented Generation) Sistemi Kurulumu
# Bu script, Paul Graham'ın makalelerini okuyup embedding'lerini oluşturur ve FAISS kullanarak bir vektör veri tabanı oluşturur.
# Ardından, bu veritabanını kullanarak kullanıcı postlarına yanıt verecek bir RAG sistemi kurar.

import os # OS = Dosya ve klasör işlemleri için, makaleleri kaydetmek için klasör oluşturmak, dosyaları yazmak için
from pathlib import Path # Path = Dosya yollarını yönetmek için, dosya ve klasör yollarını oluşturmak için
import numpy as np # NumPy = Sayısal işlemler için, embedding'leri numpy array'e dönüştürmek için, FAISS NumPy ile çalışır, Lazım
import faiss # FAISS = Facebook AI Similarity Search, embedding'leri hızlıca aramak için kullanılır, yakın metinleri bulmak için
from sentence_transformers import SentenceTransformer # SentenceTransformer = Metinleri embedding'lere dönüştürmek için
from tqdm import tqdm # tqdm = İlerleme çubuğu göstermek için, işlemlerin ilerlemesini görselleştirmek için, kullanmasan da olur 

# Makalelerin bulunduğu klasör
folder = "paul_graham_articles"

# Klasör varlığını kontrol et
if not os.path.exists(folder):
    print(f"{folder} klasörü bulunamadı!")
    exit(1)

texts = []       # Makale içeriklerini tutacak liste
filepaths = []   # Her dosyanın yolunu saklayacak liste

print(" Makaleler okunuyor...") 

# Tüm .txt dosyalarını oku
for filename in os.listdir(folder): # Klasördeki tüm dosyaları listele, txt dosyalarını bul
    if filename.endswith(".txt"): # Sadece .txt uzantılı dosyaları işle, html varsa atla
        path = os.path.join(folder, filename) # Dosya yolunu oluştur, klasör ve dosya adını birleştir, örneğin "paul_graham_articles/essay1.txt"
        try:
            with open(path, "r", encoding="utf-8") as f: # Dosyayı oku, "r" = okuma modu, encoding="utf-8" = Türkçe karakterleri düzgün okumak için
                text = f.read()
                if text.strip():  # Boş olmayan metinleri ekle
                    texts.append(text) # Metni listeye ekle
                    filepaths.append(path) # Dosya yolunu listeye ekle
                    print(f" {filename} okundu ({len(text)} karakter)")
        except Exception as e:
            print(f" {filename} okunamadı: {e}")

if not texts: # Eğer metin listesi boşsa, hiçbir makale okunamamış demektir
    print("Hiç metin dosyası bulunamadı!")
    exit(1)

print(f"\n Toplam {len(texts)} makale bulundu.")  

# SentenceTransformer modelini yükle
print("\n Embedding modeli yükleniyor (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2') # Küçük ve hızlı bir model, embedding'leri hızlıca oluşturmak için kullanılır

# Embedding'leri oluştur
print("\n Embedding'ler oluşturuluyor...")
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)   # Metinleri embedding'lere dönüştür, normalize et, ilerleme çubuğunu göster, numpy array olarak döndür

print(f"\n{len(embeddings)} embedding başarıyla oluşturuldu.")

# Embeddingleri numpy array'e çevir
embedding_matrix = np.array(embeddings).astype("float32") # FAISS için float32 formatına dönüştür, embedding'leri numpy array olarak sakla
# biz zaten array olarak aldık, ama yine de güvenli olsun diye numpy array'e çeviriyoruz
print(f" Embedding matrisi boyutu: {embedding_matrix.shape}")

# FAISS index oluştur
print("\n FAISS index oluşturuluyor...")
index = faiss.IndexFlatL2(embedding_matrix.shape[1]) # L2 normuna göre index oluştur, L2= Euclidean mesafeyi kullanarak benzerlik hesapla, sabit boyutlu vektör. 
#shape[0] = embedding sayısı, shape[1] = embedding boyutu, bize boyutu lazım, mesela 384
# IndexFlatL2 = Düz bir index, L2 normuna göre benzerlik

index.add(embedding_matrix) # Embedding'leri index'e ekle, FAISS index'e embedding'leri ekler, artık arama yapabiliriz

# FAISS indexi ve dosya yollarını kaydet
try:
    faiss.write_index(index, "paul_index.faiss") # FAISS index'i dosyaya kaydet, artık bu index'i kullanarak arama yapabiliriz
    print(" FAISS index kaydedildi: paul_index.faiss")
    
    with open("filepaths.txt", "w", encoding="utf-8") as f: # Dosya yollarını kaydet, her dosyanın yolunu filepaths.txt dosyasına yaz
        for path in filepaths: 
            f.write(path + "\n")
    print(" Dosya yolları kaydedildi: filepaths.txt")
    
    print(f"\n RAG sistemi başarıyla kuruldu!")
    print(f" {len(texts)} makale işlendi")
    print(f" {len(embeddings)} embedding oluşturuldu")
    print(f" Index boyutu: {embedding_matrix.shape}")
    print(f" Kullanılan model: all-MiniLM-L6-v2 (sentence-transformers)")
    
except Exception as e: # Hata yakala, e = hata mesajı
    print(f" Dosya kaydetme hatası: {e}")

