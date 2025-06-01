import os
import uuid
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

def index_documents(docs):
    # 1. Przygotuj klienta do embeddingów
    embedder = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_deployment="text-embedding-ada-002",
        api_version="2024-12-01-preview"
    )

    # 2. Przygotuj klienta do Azure Search
    search = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "pdf-index"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

    # 3. Stwórz dokumenty do indeksu bez `metadata`
    documents_to_upload = []
    for doc in docs:
        documents_to_upload.append({
            "id": str(uuid.uuid4()),
            "content": doc.page_content,
            "embedding": embedder.embed_query(doc.page_content)
        })

    # 4. Wyślij do Azure Search
    result = search.upload_documents(documents=documents_to_upload)
    print("Uploaded:", result)
