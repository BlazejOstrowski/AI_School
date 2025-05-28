from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
from azure.core.exceptions import ResourceNotFoundError

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY))

index_name = "pdf-index"

index = SearchIndex(
    name=index_name,
    fields=[
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="filename", type=SearchFieldDataType.String, searchable=True),
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
        algorithms=[
            HnswAlgorithmConfiguration(name="default", kind="hnsw")
        ],
        profiles=[
            VectorSearchProfile(
                name="default",
                algorithm_configuration_name="default"  # <- to jest kluczowy argument
            )
        ]
    )
)

# Usuń, jeśli już istnieje (opcjonalnie)
try:
    client.get_index(index_name)
    client.delete_index(index_name)
    print(f"Usunięto istniejący indeks: {index_name}")
except ResourceNotFoundError:
    print(f"Indeks '{index_name}' nie istnieje — tworzymy nowy.")

# Utwórz indeks
client.create_index(index)
print(f"Indeks '{index_name}' został utworzony poprawnie.")
