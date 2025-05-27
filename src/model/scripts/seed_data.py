import getpass
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_milvus import Milvus
from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from pymilvus import connections, utility
from uuid import uuid4
from dotenv import load_dotenv


# Load biến môi trường
load_dotenv()
def connect_milvus():
    try:
        connections.connect(
            alias="default",
            host="milvus-standalone",
            port="19530",
            secure=False,
        )
        print("Kết nối Milvus thành công!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")
        raise
def load_file_pdf(file_path:str):
    """
    Hàm này dùng để load file pdf từ đường dẫn file_path
    """
    loader = PyPDFLoader(file_path, extract_images=False)
    documents = loader.load()
    return documents

def seed_data_milvus_ollama(file_path:str, use_model:str,collection_name :str,url:str):
    documents = load_file_pdf(file_path)
    # Chia nhỏ văn bản thành các đoạn nhỏ (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    # Chuyển đổi `chunks` thành `Document` để lưu vào Milvus
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
    uuids = [str(uuid4()) for _ in range(len(documents))]
    # Kết nối với Milvus
    connect_milvus()
    #khởi tạo OllamaEmbeddings
    embeddings = OllamaEmbeddings(
        model=use_model,
        base_url="http://ollama:11434" 
    )
    try:
        vectorstore = Milvus(
            embedding_function=embeddings,
            collection_name=collection_name,
            drop_old=False,
            connection_args={"host": "milvus-standalone", "port": "19530"}  # Chỉ định rõ host và port
        )
        vectorstore.add_documents(documents=documents, ids = uuids)  # Thêm documents vào Milvus
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")

def delete_collection(collection_name:str):
    connect_milvus()
    utility.drop_collection(collection_name)
    print(f"Đã xóa collection {collection_name} thành công!")
