import os
import json
import fitz  # PyMuPDF
import uuid
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_output
from dotenv import load_dotenv

from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Wczytanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja
PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "pdf.pdf")
CHUNK_SIZE = 500
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
SEARCH_INDEX = "pdf-index"

AZURE_OPENAI_ENDPOINT = "https://openai-bost593.openai.azure.com"
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
EMBEDDING_DEPLOYMENT_NAME = "text-embedding-ada-002"

# Klient OpenAI
openai_client = AzureOpenAI(
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY
)

# Klient wyszukiwania
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# Chunkowanie PDF
print("[INFO] Chunking PDF...")
doc = fitz.open(PDF_PATH)
text = "".join([page.get_text() for page in doc])
words = text.split()
chunks = [" ".join(words[i:i + CHUNK_SIZE]) for i in range(0, len(words), CHUNK_SIZE)]

# Embedding + Upload
print("[INFO] Generating embeddings and uploading to Azure Search...")
documents = []
for chunk in chunks:
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT_NAME,
        input=chunk
    )
    embedding = response.data[0].embedding
    doc_id = str(uuid.uuid4())
    documents.append({
        "id": doc_id,
        "content": chunk,
        "embedding": embedding
    })

search_client.upload_documents(documents)
print(f"[DONE] Uploaded {len(documents)} chunks to Azure Search index '{SEARCH_INDEX}'.")

# Vector Query (NOWA SYNTAKSA)
print("[INFO] Running vector search...")
query_text = "What is this PDF about?"
query_embedding = openai_client.embeddings.create(
    model=EMBEDDING_DEPLOYMENT_NAME,
    input=query_text
).data[0].embedding

vector_results = search_client.search(
    search_text=None,
    vector_queries=[{
        "kind": "vector",
        "vector": query_embedding,
        "fields": "embedding",
        "k": 3
    }]
)


vector_output = [doc for doc in vector_results]

# Semantic Query
print("[INFO] Running semantic search...")
semantic_results = search_client.search(
    search_text=query_text,
    top=3
)
semantic_output = [doc for doc in semantic_results]

# Zapis do notebooka
print("[INFO] Saving results to notebook...")
notebook_path = "notebooks/queries.ipynb"
os.makedirs("notebooks", exist_ok=True)

nb = new_notebook()
nb.cells = [
    new_code_cell(source="# Vector Query Result", outputs=[
        new_output("execute_result", data={"application/json": vector_output}, execution_count=1)
    ]),
    new_code_cell(source="# Semantic Query Result", outputs=[
        new_output("execute_result", data={"application/json": json.dumps(semantic_output, indent=2)}, execution_count=2)
    ])
]

with open(notebook_path, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"[DONE] Saved query results to {notebook_path}")
