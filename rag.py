from flask import Flask, request, jsonify, session  # Flask = Web uygulamasını başlatmak için, Request = Kullanıcı verilerini almak için, jsonify = JSON cevaplarını oluşturmak için, session = Konuşma geçmişini tutmak için
from flask_cors import CORS # CORS = Cross-Origin Resource Sharing, farklı orijinlerden gelen isteklere izin vermek için
#BACKEND VE FRONTED FARKLI PORTLARDA ÇALIŞIYORSA CORS GEREKİR
from sentence_transformers import SentenceTransformer  # SentenceTransformer = Metinleri embedding'lere dönüştürmek için
# RAG İÇİN GEREKLİ, SORUYU VE PAUL GRAHAM'IN MAKALELERİNİ EMBEDDING'E DÖNÜŞTÜRMEK İÇİN, HEPSİNİ SAYISAL BİR VECTÖR HALİNE GETİRİR
import faiss # FAISS = Facebook AI Similarity Search, embedding'leri hızlıca aramak için kullanılır, yakın metinleri bulmak için
import numpy as np # NumPy = Sayısal işlemler için, embedding'leri numpy array'e dönüştürmek için, FAISS NumPy ile çalışır, Lazım

from openai import OpenAI # OpenAI = OpenAI API'yi kullanmak için, GPT-3.5 modeline erişmek için
import os # OS = API anahtarını okumak için, .env dosyasından API anahtarını almak için
from dotenv import load_dotenv # Load dotenv = .env dosyasını python uygulamasına yüklemek için
load_dotenv() # .env dosyasını yükle, API anahtarını almak için 

# FAISS ve embedding modelini yükle
model = SentenceTransformer('all-MiniLM-L6-v2') #KÜÇÜK MODEL, HIZLI VE ETKİLİ
index = faiss.read_index("paul_index.faiss") # FAISS indexi oku, embedding'leri hızlıca aramak için, vektör veri tabanını içerir

# Makale yollarını oku 
with open("filepaths.txt", "r", encoding="utf-8") as f: # Okuma işlemi, filepaths.txt dosyasından makale yollarını oku, "utf-8" Türkçe karakterleri düzgün okusun diye
    filepaths = [line.strip() for line in f.readlines()]   # Her satırı oku ve boşlukları temizle

# Flask başlat
app = Flask(__name__) # Flask uygulamasını başlat, __name__ = Ana modül adı, Flask uygulamasının ismi
app.secret_key = 'xxxxxxxxxx'  # Session için gerekli
CORS(app, supports_credentials=True) # CORS'u etkinleştir, farklı orijinlerden gelen isteklere izin ver

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # OpenAI API istemcisini başlat, .env dosyasından API anahtarını al, oku, nesne OpenAI istemcisi

@app.route("/chat", methods=["POST"]) # /chat adresine POST isteği geldiğinde bu fonksiyonu çağır
def chat(): 
    user_message = request.json.get("message", "")  #Frontend'den gelen JSON verisini al, "message" anahtarını kullanarak kullanıcı mesajını al, yoksa boş bir mesaj al

    # Session'dan konuşma geçmişini al
    if 'conversation_history' not in session:
        session['conversation_history'] = []
        session['current_context'] = None

    # Eğer bu ilk mesajsa veya konuşma geçmişi boşsa, yeni arama yap
    if not session['conversation_history']:
        # Embedle
        query_embedding = model.encode([user_message], normalize_embeddings=True) # Kullanıcı mesajını embedding'e dönüştür, normalize et, embedding'ler sayısal vektörlerdir, normalize etmek aynı uzunlukta yapmak demektir, FAISS için uygun hale getirir
        
        # FAISS ile en yakın metni bul
        top_k = 1 # En yakın 1 metni bul, top_k = 1, sadece en yakın metni alacağız
        D, I = index.search(np.array(query_embedding).astype("float32"), top_k) # FAISS indexinde arama yap, D = mesafe, I = indeks numaraları, embedding'i float32 olarak dönüştür, FAISS bu formatı kullanır
        top_idx = I[0][0] # En yakın metnin indeksini al, I[0][0] = ilk (ve tek) en yakın metnin indeks numarası
        file_path = filepaths[top_idx] # En yakın metnin dosya yolunu al, filepaths listesinden indeks numarasına göre dosya yolunu al

        with open(file_path, "r", encoding="utf-8") as f: # En yakın metin dosyasını oku, "utf-8" Türkçe karakterleri düzgün okusun diye
            context_text = f.read() # Dosya içeriğini oku, context_text = makale içeriği
        
        session['current_context'] = context_text
    else:
        # Konuşma devam ediyorsa, mevcut context'i kullan
        context_text = session['current_context']

    # Konuşma geçmişini oluştur
    messages = [
        {"role": "system", "content": f"You are Paul Graham. Use the following article as context to answer:\n\n{context_text}"}
    ]
    
    # Önceki konuşma geçmişini ekle
    for msg in session['conversation_history']:
        messages.append(msg)
    
    # Kullanıcının yeni mesajını ekle
    messages.append({"role": "user", "content": user_message})

    # GPT'ye kontekstle birlikte gönder
    response = client.chat.completions.create( # OpenAI API'ye istek at, chat completion oluştur
        model="gpt-3.5-turbo", # Modeli belirle, gpt-3.5-turbo modeli kullanılıyor
        messages=messages  # Prompt engineering, mesajları ayarla
    )

    reply = response.choices[0].message.content # 0 olmasının sebebi, OpenAI API'sinin birden fazla cevap dönebilmesi, ancak biz ilk cevabı alıyoruz, en ilgilisi o, reply = modelin cevabı
    
    # Konuşma geçmişini güncelle
    session['conversation_history'].append({"role": "user", "content": user_message})
    session['conversation_history'].append({"role": "assistant", "content": reply})
    

    return jsonify({"reply": reply}) # JSON cevabı olarak döndür, {"reply": modelin cevabı}

@app.route("/reset", methods=["POST"]) # Yeni konuşma başlatmak için
def reset_conversation():
    session['conversation_history'] = []
    session['current_context'] = None
    return jsonify({"message": "Conversation reset"})

if __name__ == "__main__": # Eğer bu dosya doğrudan çalıştırılırsa, Flask uygulamasını başlat
    app.run(debug=True) 
