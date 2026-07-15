import os
import shutil
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()
#PGVECTOR
CONNECTION_STRING = os.environ["PG_CONNECTION"]
COLLECTION_NAME = "lumenist"

embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


loader = DirectoryLoader(
    path="docs",
    glob="**/*.txt",
    loader_cls=TextLoader
)


documents = loader.load()


# tag each document with its department from subfolder name
for doc in documents:
    source_path =doc.metadata.get("source", "")
    parts = source_path.replace("\\","/").split("/")

    if len(parts)>= 3:
        doc.metadata["department"] = parts[-2]
    else:
        doc.metadata["department"] ="ALL"

    doc.metadata["source"] = parts[-1] if parts else source_path

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

# stor in pgvector -drop and recreate collection for fresh ingest
vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    pre_delete_collection=True  # clears existing data before reinserting
)
print(f"Stored{len(chunks)} chunks in pgvector")
for i, chunk in enumerate(chunks):
    print(f"chunk {i}: dept={chunk.metadata.get('department')} source={chunk.metadata.get('source')}")


