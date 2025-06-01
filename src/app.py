import streamlit as st
import requests

st.set_page_config(page_title="RAG App", page_icon="🧠")

st.title("🔍 RAG Q&A with Azure Function")

# --- Zadawanie pytań ---
st.header("Ask your PDF knowledge base")

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query:
        with st.spinner("Thinking..."):
            response = requests.get("http://localhost:7071/api/ask_rag", params={"query": query})
            if response.status_code == 200:
                json_data = response.json()
                st.success(json_data["answer"])
                st.caption(f"Trace ID: {json_data.get('traceId')}")
            else:
                st.error("Error from backend: " + response.text)
    else:
        st.warning("Please enter a question.")

# --- Upload PDF ---
st.header("📄 Upload new PDF to index")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Upload and index"):
        with st.spinner("Uploading and processing..."):
            files = {"file": uploaded_file.getvalue()}
            response = requests.post("http://localhost:7071/api/upload_pdf", files=files)
            if response.status_code == 200:
                st.success(response.text)
            else:
                st.error("Upload failed: " + response.text)

# --- TEST BŁĘDU ---
st.header("💥 Test Application Insights Logging")

if st.button("Raise error"):
    with st.spinner("Calling error endpoint..."):
        response = requests.get("http://localhost:7071/api/raise_error")
        if response.status_code == 500:
            st.error("Intentional error triggered. Check Application Insights.")
        else:
            st.success(response.text)
