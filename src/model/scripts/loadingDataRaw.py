from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

def loadingDataRaw(pdf_path, db_path="db"):
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Chia nhỏ văn bản
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # Tạo vector embedding
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    vector_db = Chroma(persist_directory=db_path, embedding_function=embedding_model)

    # Thêm dữ liệu vào database
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    vector_db.add_texts(texts, metadatas=metadatas)

    # Lưu database
    vector_db.persist()

    print("✅ Đã nạp dữ liệu PDF vào database!")

    return vector_db

# Gọi hàm với file PDF cụ thể
vector_db = loadingDataRaw("./BAI-GIANG-LSĐ-2021.pdf")
