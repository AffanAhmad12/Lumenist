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
