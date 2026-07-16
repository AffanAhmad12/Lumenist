import os 
import csv
from huggingface_hub import InferenceClient
from retriever import retrieve_with_confidence
from dotenv import load_dotenv
from datetime import datetime
from langdetect import detect
from deep_translator import GoogleTranslator
from history import save_message

load_dotenv()

client=InferenceClient(token=os.environ["HF_TOKEN"])

SYSTEM_PROMPT = """ You are an internal HR policy assistant for Lumelight. You answer employee question \
using ONLY the policy excerpts provided as context. THese policies contain precise numbers \
(days, percentage, deadlines) and clauses references - accuracy on these specifics is critical.

Rules:
1. Answer using ONLY information in the context below. Do not use outside knowledge.
2.If the context does not contain enough information to answer, say: \
"I don't have enough information in the policy documents to answer this confidently.Please contaict HR."
3.When the answer involves a number (days, percentage , amount), state it exactly as written in the context.
4.If multiple policies in the context seem relevant , mention which policy each part of your answer comes from \
(e.g. , "Per the Leave Policy...").
5.Keep answers concise and direct  - 2-4 sentences unless the question needs a list.
6.Do not give legal advice or interpret ambiguous policy gaps ; just state what the polict says."""

USER_PROMPT_TEMPLATE="""CONTEXT:
{context}

Question:{query}

Answer based strictly on the context above:"""

LOG_FILE = os.path.join(os.path.dirname(__file__),"..", "knowledge_gaps.csv")

#knowledge gaps
def log_knowledge_gap(query, username):
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a" , newline="", encoding="utf-8")as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "username", "question"])

        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now(). strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "question": query
        })
def translate(text, source="auto", target="en"):
    """Translate  text from source language to target language."""
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text   # return original if translation fails

def answer_question(query, username="Anonymous", role="ALL"):
    # detect language and translate query to English
    try:
         # only detect language for longer queries — short ones default to English
        if len(query.strip()) < 20:
            detected_lang = "en"
            is_english = True
        else:
            detected_lang = detect(query)
            is_english = detected_lang == "en"
    except:
        detected_lang = "en"
        is_english = True
    if  not is_english:
        english_query = translate(query, source="auto", target="en")
    else:
        english_query= query
     # use english query for retrieval
    results= retrieve_with_confidence(english_query, role=role)

    if results is None:
        log_knowledge_gap(query, username) # log original query, not translated
        return{
            "answer": "I don't have enough relevant information to answer confidently. Please contact a Human",
            "sources": []
        }
    context = "\n\n".join([doc.page_content for doc , score in results])
    sources= [doc.metadata.get("source")for doc , score in results]

    response = client.chat_completion(
        messages=[
            {"role": "system","content": SYSTEM_PROMPT},
            {"role":"user", "content": USER_PROMPT_TEMPLATE.format(context=context, query=query)}
        ],
       model="meta-llama/Llama-3.1-8B-Instruct",
       max_tokens=200,
       temperature=0.1
    )

    answer = response.choices[0].message.content
    
     # translate answer back to user's language
    if not is_english:
        answer = translate(answer, source="en", target=detected_lang) 
      # translate answer back to user's language
    if not is_english:
        answer = translate(answer, source="en", target= detected_lang)
      #Save to persistent history
    save_message(username, query, answer, sources)

    return {
        "answer": answer,
        "sources":sources
    }
if __name__ == "__main__":
    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        results = answer_question(query, username="terminal_test")
        print(f"\nAnswer: {results['answer']}")
        print(f"Sources: {results['sources']}")
