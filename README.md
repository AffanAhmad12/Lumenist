# Lumenist - AI Powered HR Policy Chatbot

An internal HR policy RAG (Retrieval-Augmented Generation) chatbot built for Lumelight x CxC Infotech Pvt. Ltd.

## Features
- Natural language Q&A on HR policy documents
- Role-based access control (HR, Finance, IT, BPO, LPO, Interns, Admin)
- Multilingual support (Hindi, Urdu, French, Spanish, and more)
- Voice input via microphone
- Knowledge gap logging to CSV
- Document upload with department tagging
- Chat history in sidebar
- Secure login with username and password

## Tech Stack
- **LLM:** Meta Llama 3.1 8B via HuggingFace Inference API
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **Vector Database:** pgvector + PostgreSQL
- **Framework:** LangChain
- **UI:** Streamlit
- **Language Detection:** langdetect + deep-translator

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/AffanAhmad12/Lumenist.git
cd Lumenist
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy `.env.example` to `.env` and fill in your values:

### 5. Set up PostgreSQL with pgvector
- Install PostgreSQL 18
- Install pgvector extension
- Create database: `CREATE DATABASE lumenist;`
- Enable extension: `CREATE EXTENSION vector;`

### 6. Ingest documents
```bash
python src/ingest.py
```

### 7. Run the app
```bash
streamlit run src/app.py
```
## How it Works
1. Documents are chunked, embedded, and stored in pgvector
2. User logs in with role-based credentials
3. Question is detected for language and translated to English if needed
4. Relevant chunks are retrieved based on semantic similarity and role permissions
5. LLM generates a grounded answer using only retrieved context
6. Answer is translated back to user's original language
7. Unanswered questions are logged to knowledge_gaps.csv


## Project Structure
Lumenist/
├── docs/
│   ├── All/          # Documents accessible to all roles
│   ├── HR/           # HR-only documents
│   ├── Finance/      # Finance-only documents
│   └── Interns/      # Intern documents
├── src/
│   ├── app.py        # Streamlit UI
│   ├── chat.py       # LLM answer generation
│   ├── retriever.py  # pgvector similarity search
│   ├── ingest.py     # Document ingestion
│   ├── ingest_upload.py  # Runtime document upload
│   └── auth.py       # Authentication
├── config/
│   ├── users.json    # User credentials
│   └── roles.json    # Role-department mapping
├── .env.example
└── requirements.txt
