import os
import uuid
import fitz  # PyMuPDF
import nbformat
from nbformat.v4 import new_code_cell
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile
)
from openai import AzureOpenAI

# Wczytaj zmienne
load_dotenv()
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Parametry
INDEX_NAME = "pdf-index"
PDF_FOLDER = os.path.join(os.path.dirname(__file__), "..", "brochures")
CHUNK_SIZE = 500
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_DEPLOYMENT = "gpt-4o"
NOTEBOOK_PATH = os.path.join("..", "notebooks", "queries.ipynb")

# Klienci
openai_client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version="2024-12-01-preview"
)
search_admin = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))
search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))

# Tworzenie indeksu
def create_index():
    if INDEX_NAME in [i.name for i in search_admin.list_indexes()]:
        print("Indeks już istnieje — usuwam...")
        search_admin.delete_index(INDEX_NAME)

    index = SearchIndex(
        name=INDEX_NAME,
        fields=[
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="filename", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="default"
            )
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default")],
            profiles=[VectorSearchProfile(name="default", algorithm_configuration_name="default")]
        )
    )
    search_admin.create_index(index)
    print("Utworzono indeks:", INDEX_NAME)

# Chunkowanie PDF-a
def extract_chunks_from_pdf(path, chunk_size=CHUNK_SIZE):
    doc = fitz.open(path)
    text = "".join([page.get_text() for page in doc])
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Indeksowanie folderu PDF
def index_documents_from_folder(folder):
    docs = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder, filename)
            chunks = extract_chunks_from_pdf(path)
            print(f"{filename} → {len(chunks)} chunks")

            for chunk in chunks:
                embedding = openai_client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=chunk
                ).data[0].embedding
                docs.append({
                    "id": str(uuid.uuid4()),
                    "filename": filename,
                    "content": chunk,
                    "embedding": embedding
                })

    result = search_client.upload_documents(documents=docs)
    print("Zaindeksowano:", len(docs))

# Zapisywanie do notebooka
def save_to_notebook(question, vector_answer, semantic_answer):
    os.makedirs(os.path.dirname(NOTEBOOK_PATH), exist_ok=True)
    if os.path.exists(NOTEBOOK_PATH):
        with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
    else:
        nb = nbformat.v4.new_notebook()

    nb.cells.append(new_code_cell(f"# Question: {question}\n\n## Vector Result:\n```json\n{vector_answer}\n```"))
    nb.cells.append(new_code_cell(f"## Semantic Result:\n```json\n{semantic_answer}\n```"))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

# Interaktywna sesja pytań
def ask_questions():
    while True:
        q = input("\nTwoje pytanie ('exit' aby zakończyć): ")
        if q.lower() in ["exit", "quit"]:
            break

        prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": q}
        ]

        vector_query = {
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": SEARCH_ENDPOINT,
                        "index_name": INDEX_NAME,
                        "authentication": {"type": "api_key", "key": SEARCH_KEY},
                        "query_type": "vector",
                        "embedding_dependency": {"type": "deployment_name", "deployment_name": EMBEDDING_MODEL},
                        "top_n_documents": 5
                    }
                }
            ]
        }

        semantic_query = {
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": SEARCH_ENDPOINT,
                        "index_name": INDEX_NAME,
                        "authentication": {"type": "api_key", "key": SEARCH_KEY},
                        "query_type": "simple"
                    }
                }
            ]
        }

        vector_response = openai_client.chat.completions.create(
            model=CHAT_DEPLOYMENT,
            messages=prompt,
            extra_body=vector_query
        ).choices[0].message.content

        semantic_response = openai_client.chat.completions.create(
            model=CHAT_DEPLOYMENT,
            messages=prompt,
            extra_body=semantic_query
        ).choices[0].message.content

        print("\nVector:", vector_response)
        print("\nSemantic:", semantic_response)
        save_to_notebook(q, vector_response, semantic_response)

# === Wykonanie ===
if __name__ == "__main__":
    create_index()
    index_documents_from_folder(PDF_FOLDER)
    ask_questions()
