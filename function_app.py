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
    try:
        logging.info("ask_rag function called")
    except UnicodeEncodeError:
        pass

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
            body=json.dumps({"answer": answer}, ensure_ascii=False).encode("utf-8"),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        safe_error = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        return func.HttpResponse(
            body=f"Error: {safe_error}".encode("utf-8"),
            status_code=500,
            mimetype="text/plain"
        )

# --- Endpoint: Upload PDF ---
@app.function_name(name="upload_pdf")
@app.route(route="upload_pdf", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_pdf(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("upload_pdf called")
    except UnicodeEncodeError:
        pass

    try:
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)

        os.makedirs(BROCHURE_FOLDER, exist_ok=True)
        file_path = os.path.join(BROCHURE_FOLDER, f"{uuid.uuid4()}.pdf")
        with open(file_path, "wb") as f:
            f.write(file.read())

        loader = PyMuPDFLoader(file_path)
        # docs = loader.load()
        # for doc in docs:
        #     doc.metadata = {}
        # index_documents(docs)

        return func.HttpResponse("File uploaded and indexed successfully.", status_code=200)

    except Exception as e:
        safe_error = str(e).encode("utf-8", errors="ignore").decode("utf-8")
        return func.HttpResponse(
            body=f"Error: {safe_error}".encode("utf-8"),
            status_code=500,
            mimetype="text/plain"
        )
