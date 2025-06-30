# VELA-CASE
#  Paul Graham RAG Chatbot

This is a Retrieval-Augmented Generation (RAG) chatbot that answers user questions using the essays of Paul Graham. It fetches the most relevant essay using vector similarity (FAISS) and responds in Paul Graham's style using OpenAI's GPT model.

---

##  Features

-  Uses **RAG architecture** (semantic search + LLM generation)
-  Scrapes and indexes **Paul Graham's essays**
-  Fast similarity search using **FAISS**
-  Generates context-aware responses with **OpenAI GPT-3.5**
-  Frontend chat interface (HTML + JavaScript)
-  Conversation memory with Flask session

---

##  Tools & Libraries Used

| Tool/Library           | Purpose                                |
|------------------------|----------------------------------------|
| `Flask`                | Backend web framework                  |
| `Flask-CORS`           | Enable cross-origin requests           |
| `SentenceTransformers` | Embedding texts (MiniLM-L6-v2)         |
| `FAISS`                | Vector similarity search               |
| `OpenAI`               | LLM for response generation            |
| `BeautifulSoup`        | Web scraping Paul Graham essays        |
| `tqdm`                 | Progress bar during embedding          |
| `dotenv`               | Load OpenAI API key from `.env`        |

---

##  Project Structure

```
.
├── articles.py              # Web scraping Paul Graham's essays
├── db.py                    # Creates FAISS index and filepaths
├── rag.py                   # Main backend Flask app with RAG logic
├── filepaths.txt            # Saved essay paths
├── paul_index.faiss         # FAISS vector index
├── paul_graham_articles/    # Folder with scraped .txt essays
├── templates/
│   └── index.html           # Chat frontend (input/output)
└── README.md                # This file
```

---

## ⚙ Installation & Setup

1. **Clone this repository**  
   ```bash
   git clone https://github.com/zengelkaan/VELA-CASE.git
   cd VELA-CASE.git
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key**  
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=***********
   ```

---

##  Running the System

### 1. Scrape essays *(Run once)*  
```bash
python articles.py
```

### 2. Create vector index *(Run once)*  
```bash
python db.py
```

### 3. Start the backend server  
```bash
python rag.py
```

It will run at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 4. Open `index.html` in browser  
Located in `templates/index.html` or your chosen frontend folder.

---

##  Example Questions to Try

- "Why does Paul Graham believe in working on your own projects?"
- "What does he mean by founder mode?"
- "How does Paul Graham define wealth?"

---

##  Notes

- The system uses session-based memory, so follow-up questions will maintain context.
- You can reset the conversation by sending a POST request to `/reset`.

---

##  Contact

Developed by Kaan Zenğel. 
kaan.zengel@sabanciuniv.edu
