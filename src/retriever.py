import os
import psycopg2
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()
#PGVECTOR
CONNECTION_STRING= os.environ["PG_CONNECTION"]
COLLECTION_NAME = "lumenist"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def get_allowed_departments(role):
    """Load allowed departments for a role from database """
    try:
        conn_str = os.environ["PG_CONNECTION"].replace("postgresql+psycopg://","postgresql://")
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute(
            "SELECT allowed_departments From roles WHERE role_name=%s",
            (role.upper(),)   
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0].split(",")
        return ["ALL"]
    except Exception as e:
        print(f"ROLE fetch error: {e}")
        return ["ALL"]

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
