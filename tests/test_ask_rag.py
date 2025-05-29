import pytest
from src.ask_rag import ask_rag

def test_valid_query():
    result = ask_rag("What is Azure AI Search?")
    assert isinstance(result, str)
    assert len(result) > 0

def test_empty_query_raises():
    with pytest.raises(Exception):
        ask_rag("")
