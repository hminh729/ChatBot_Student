# Import các thư viện cần thiết =====
import getpass
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from pymilvus import connections, utility
from uuid import uuid4
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Hàm kết nối Milvus
def connect_milvus():
    try:
        # Kết nối đến Milvus bằng địa chỉ nội bộ của container Docker
        connections.connect(
            alias="default",
            host="milvus-standalone",  # tên service trong docker-compose
            port="19530",
            secure=False,
        )
        print("Kết nối Milvus thành công!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")
        raise

# Hàm đọc nội dung từ file PDF
def load_file_pdf(file_path: str):
    """
    Dùng PyPDFLoader để tải nội dung từ file PDF.
    """
    loader = PyPDFLoader(file_path, extract_images=False)
    documents = loader.load()
    return documents

# Hàm xử lý, tạo embedding và lưu dữ liệu vào Milvus
def seed_data_milvus_ollama(file_path: str, use_model: str, collection_name: str, url: str):
    """
    - Đọc file PDF và chia nhỏ nội dung
    - Dùng model Ollama để tạo embedding
    - Lưu vào vectorstore Milvus
    """
    # Load file PDF thành các Document
    documents = load_file_pdf(file_path)

    # Chia văn bản thành các đoạn nhỏ (chunk)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # Tạo lại các Document có metadata chuẩn hóa
    documents = [
        Document(
            page_content=chunk.page_content,
            metadata={
                'author': chunk.metadata.get('author', ''),
                'content_type': chunk.metadata.get('content_type', 'pdf'),
                'keywords': chunk.metadata.get('keywords', ''),
                'subject': chunk.metadata.get('subject', ''),
                'title': chunk.metadata.get('title', ''),
                'total_pages': chunk.metadata.get('total_pages', 0),
                'page': chunk.metadata.get('page', 0),
                'page_label': chunk.metadata.get('page_label', 0),
            }
        )
        for chunk in chunks
    ]

    # Tạo UUID cho từng Document
    uuids = [str(uuid4()) for _ in range(len(documents))]

    # Kết nối tới Milvus
    connect_milvus()

    # Khởi tạo embedding model Ollama
    embeddings = OllamaEmbeddings(
        model=use_model,  # ví dụ: "bge-m3:567m"
        base_url="http://ollama:11434"  # URL local của Ollama server
    )

    try:
        # Tạo hoặc kết nối tới collection trên Milvus
        vectorstore = Milvus(
            embedding_function=embeddings,
            collection_name=collection_name,
            drop_old=False,
            connection_args={"host": "milvus-standalone", "port": "19530"}
        )

        # Thêm dữ liệu vào Milvus
        vectorstore.add_documents(documents=documents, ids=uuids)
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")

# Hàm xoá collection trong Milvus
def delete_collection(collection_name: str):
    """
    Xoá collection (bộ dữ liệu vector) trong Milvus.
    """
    connect_milvus()
    utility.drop_collection(collection_name)
    print(f"Đã xóa collection {collection_name} thành công!")
