import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()
#PGVECTOR
CONNECTION_STRING= os.environ["PG_CONNECTION"]
COLLECTION_NAME = "lumenist"

ROLES_FILE = os.path.join(os.path.dirname(__file__),"..", "config", "roles.json")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def get_allowed_departments(role):
    """Load roles.json and return the list of departments this role can access. """
    with open(ROLES_FILE, "r")as f:
        roles=json.load(f)
    return roles.get(role.upper(), ["ALL"])

def get_vectordb():
    #PGVECTOR
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING
    )

def retrieve_with_confidence(query, role="ALL", threshold=0.70, k=4):
    vectordb = get_vectordb()
    allowed = get_allowed_departments(role)

    results = vectordb.similarity_search_with_score(query, k=k * 3)


    filtered = [
        (doc, score) for doc, score in results
        if doc.metadata.get("department", "ALL").upper() in [d.upper() for d in allowed]
    ]
    filtered = sorted(filtered, key=lambda x: x[1])

    
    if not filtered or filtered[0][1] > threshold:
        return None

    return filtered[:k]



if __name__=="__main__":
    vectordb = get_vectordb()
    print("Connected to pgvector successfully")

    while True:
        query = input("\nAsk a question (or type 'exit):")
        if query.lower() == "exit":
            break
        role = input("Enter role(HR/Finance/Admin etc):")
        results = retrieve_with_confidence(query,role=role)

        if results is None:
            print("No confident match found or access denied.")
        else:
            for doc , score in results:
                print(f"\nScore :{score}")
                print(f"Dept: {doc.metadata.get('department')}")
                print(f"Sources: {doc.metadata.get('source')}")
                print(f"Content: {doc.page_content[:200]}")
