from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, VectorSearch, VectorSearchProfile, VectorSearchAlgorithmConfiguration
)
from dotenv import load_dotenv
import os

load_dotenv()

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = "pdf-index"

index_client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_key))

fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String"),
    SimpleField(name="embedding", type="Collection(Edm.Single)", searchable=True)
]

vector_search = VectorSearch(
    profiles=[
        VectorSearchProfile(name="default", algorithm_configuration_name="my-hnsw")
    ],
    algorithm_configurations=[
        VectorSearchAlgorithmConfiguration(name="my-hnsw", kind="hnsw")
    ]
)

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

index_client.create_index(index)
print(f"[DONE] Index '{index_name}' created.")
