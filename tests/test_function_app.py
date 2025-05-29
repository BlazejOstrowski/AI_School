import azure.functions as func
from function_app import ask_rag_http
from unittest.mock import patch
import json

def test_ask_rag_http_success():
    req = func.HttpRequest(
        method='GET',
        url='/api/ask_rag',
        body=None,
        params={'query': 'Who is the president of Poland?'}
    )

    with patch("function_app.ask_rag", return_value="Andrzej Duda"):
        response = ask_rag_http(req)
        body = json.loads(response.get_body())

        assert response.status_code == 200
        assert body["answer"] == "Andrzej Duda"
