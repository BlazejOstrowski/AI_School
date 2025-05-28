import os
import uuid
import fitz  # PyMuPDF
import nbformat
from nbformat.v4 import new_code_cell
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyMuPDFLoader

# Wczytaj zmienne środowiskowe
load_dotenv()
os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = os.getenv("AZURE_SEARCH_ENDPOINT").replace("https://", "").split(".")[0]
os.environ["AZURE_AI_SEARCH_INDEX_NAME"] = os.getenv("AZURE_SEARCH_INDEX_NAME", "pdf-index")
os.environ["AZURE_AI_SEARCH_API_KEY"] = os.getenv("AZURE_SEARCH_KEY")

# Parametry
INDEX_NAME = os.environ["AZURE_AI_SEARCH_INDEX_NAME"]
PDF_FOLDER = os.path.join(os.path.dirname(__file__), "..", "brochures")
NOTEBOOK_PATH = os.path.join("..", "notebooks", "queries.ipynb")
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_DEPLOYMENT = "gpt-4o"

# Wczytanie i podział PDF na dokumenty LangChain
def load_documents_from_folder(folder):
    documents = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder, filename)
            loader = PyMuPDFLoader(path)
            docs = loader.load()
            for doc in docs:
                doc.metadata = {}  # Wymagane przez Azure Search
            documents.extend(docs)
    return documents

# Funkcja: zapis odpowiedzi do notebooka
def save_to_notebook(question, answer):
    os.makedirs(os.path.dirname(NOTEBOOK_PATH), exist_ok=True)
    if os.path.exists(NOTEBOOK_PATH):
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
    else:
        nb = nbformat.v4.new_notebook()

    nb.cells.append(new_code_cell(f"# Question: {question}\n\n## Answer:\n```\n{answer}\n```"))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

# Funkcja: zapytanie RAG
def ask_rag(query):
    retriever = AzureAISearchRetriever(
        content_key="content",
        top_k=3,
        index_name=INDEX_NAME
    )

    llm = AzureChatOpenAI(
        azure_deployment=CHAT_DEPLOYMENT,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-12-01-preview"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=False
    )

    result = qa_chain.invoke({"query": query})
    answer = result.get("result", result)
    print("\nAnswer:", answer)
    save_to_notebook(query, answer)
    return answer

# === Wykonanie ===
if __name__ == "__main__":
    while True:
        q = input("\nTwoje pytanie ('exit' aby zakończyć): ")
        if q.lower() in ["exit", "quit"]:
            break
        ask_rag(q)
