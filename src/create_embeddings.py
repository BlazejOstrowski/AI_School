import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.documents import Document

load_dotenv()


def index_documents(documents):
    # Usuń wszystkie niedozwolone pola
    cleaned_docs = []
    for doc in documents:
        cleaned_docs.append(Document(
            page_content=doc.page_content,
            metadata={}
        ))

    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        azure_deployment="text-embedding-ada-002",
        api_version="2024-12-01-preview"
    )

    search = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME", "pdf-index"),
        embedding_function=embeddings.embed_query,
    )

    search.add_documents(cleaned_docs)