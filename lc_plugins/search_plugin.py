
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_DEPLOYMENT = "gpt-4o"
INDEX_NAME = "pdf-index"

openai_client = AzureOpenAI(
    api_key=OPENAI_KEY,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version="2024-12-01-preview"
)

def langchain_search_plugin(query: str) -> str:
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]
    extra = {
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
    return openai_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=prompt,
        extra_body=extra
    ).choices[0].message.content
