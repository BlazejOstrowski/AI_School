import azure.functions as func
import logging
import json
from src.ask_rag import ask_rag

app = func.FunctionApp()

@app.function_name(name="ask_rag")
@app.route(route="ask_rag", auth_level=func.AuthLevel.ANONYMOUS)
def ask_rag_http(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('ask_rag function called')

    query = req.params.get("query")
    if not query:
        try:
            req_body = req.get_json()
            query = req_body.get("query")
        except ValueError:
            return func.HttpResponse("Missing 'query' parameter", status_code=400)

    if not query:
        return func.HttpResponse("Missing 'query' parameter", status_code=400)

    try:
        answer = ask_rag(query)
        return func.HttpResponse(json.dumps({"answer": answer}), mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
