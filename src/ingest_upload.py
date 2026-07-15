import os 
import tempfile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()

CONNECTION_STRING = os.environ["PG_CONNECTION"]
COLLECTION_NAME = "lumenist"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def load_file(file_path, file_extension):
    """Pick the right loader based on file type. """
    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif  file_extension ==".docx":
        loader = Docx2txtLoader(file_path)
    elif file_extension == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type:{file_extension}")
    return loader.load()
ROLE_TO_DEPT ={
    "ADMIN":"ALL",
    "HR": "HR",
    "FINANCE": "FINANCE",
    "INTERNS":"INTERNS",
}
def process_upload_files(uploaded_files, role ="ALL"):
    """ 
    Takes Streamlit UploadedFile objects, extract text , chunks it,
    and adds the chunks into the existing Chroma vectorestore.
    Returns a summary of what was added 
    """

    dept = ROLE_TO_DEPT.get(role.upper(),"ALL")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = PGVector(
        collection_name=COLLECTION_NAME,
        embeddings=embeddings,
        connection=CONNECTION_STRING,
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP
    )

    summary =[]

    for uploaded_file in uploaded_files:
        file_extension =os.path.splitext(uploaded_file.name)[1].lower()

        with tempfile.NamedTemporaryFile(delete=False ,  suffix=file_extension) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        try:
            documents = load_file(tmp_path, file_extension)
            
            for doc in documents:
                doc.metadata["source"] = uploaded_file.name
                doc.metadata["department"] = dept
            
            chunks = splitter.split_documents(documents)
            vectorstore.add_documents(chunks)

            summary.append({"file": uploaded_file.name, "chunks_added": len(chunks), "department": role.upper()})
        finally:
            os.remove(tmp_path)
    return summary
