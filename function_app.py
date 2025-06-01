import json
import os
import uuid
import logging
from pathlib import Path
import azure.functions as func
from src.ask_rag import ask_rag
from langchain_community.document_loaders import PyMuPDFLoader
from src.create_embeddings import index_documents

app = func.FunctionApp()

BROCHURE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "brochures")

# --- Endpoint: Zadawanie pytania ---
@app.function_name(name="ask_rag")
@app.route(route="ask_rag", auth_level=func.AuthLevel.ANONYMOUS)
def ask_rag_http(req: func.HttpRequest) -> func.HttpResponse:
    trace_id = str(uuid.uuid4())
    logging.info(f"[{trace_id}] ask_rag function called")

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
        return func.HttpResponse(
            body=json.dumps({"answer": answer, "traceId": trace_id}, ensure_ascii=False).encode("utf-8"),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.exception(f"[{trace_id}] Error in ask_rag")
        return func.HttpResponse(
            body=f"Error: {str(e)}".encode("utf-8"),
            status_code=500,
            mimetype="text/plain"
        )

# --- Endpoint: Upload PDF ---
@app.function_name(name="upload_pdf")
@app.route(route="upload_pdf", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_pdf(req: func.HttpRequest) -> func.HttpResponse:
    trace_id = str(uuid.uuid4())
    logging.info(f"[{trace_id}] upload_pdf called")

    try:
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)

        os.makedirs(BROCHURE_FOLDER, exist_ok=True)
        file_path = os.path.join(BROCHURE_FOLDER, f"{uuid.uuid4()}.pdf")
        with open(file_path, "wb") as f:
            f.write(file.read())

        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        # Usuń metadata przed przekazaniem do indeksowania
        for doc in docs:
            doc.metadata = None

        index_documents(docs)

        return func.HttpResponse(f"File uploaded and indexed successfully. TraceId: {trace_id}", status_code=200)

    except Exception as e:
        logging.exception(f"[{trace_id}] Error in upload_pdf")
        return func.HttpResponse(
            body=f"Error: {str(e)}".encode("utf-8"),
            status_code=500,
            mimetype="text/plain"
        )

# --- Endpoint: Raise error intentionally ---
@app.function_name(name="raise_error")
@app.route(route="raise_error", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def raise_error(req: func.HttpRequest) -> func.HttpResponse:
    trace_id = str(uuid.uuid4())
    logging.error(f"[{trace_id}] raise_error called – intentional error")
    raise Exception(f"[{trace_id}] This is a test exception for Application Insights")
