import fitz  # PyMuPDF
from langchain_milvus import Milvus
import os
from langchain_ollama import OllamaEmbeddings 
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
from pymilvus import connections
import uuid
from openai import OpenAI

def load_pdf_pymupdf(pdf_path):
    """ Đọc file PDF bằng PyMuPDF và chuyển thành dạng Document của LangChain """
    docs = []
    doc = fitz.open(pdf_path) #Mở file PDF
    for page in doc:  
        text = page.get_text("text")  #Lấy nội dung văn bản
        metadata = {"page": page.number + 1}  #Thêm metadata (số trang)
        docs.append(Document(page_content=text, metadata=metadata))
    return docs

#Đọc file PDF
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "..", "data")
pdf_path = os.path.join(data_dir, "BAI-GIANG-LSĐ-2021.pdf")

loader = load_pdf_pymupdf(pdf_path)

#Chia nhỏ văn bản để xử lý tốt hơn trong LangChain
text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=500)
split_docs = text_splitter.split_documents(loader)

print(f"Chia thành {len(split_docs)} đoạn nhỏ")

#Tạo vector từ văn bản
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# #Lưu vector vào database ChromaDB
# chroma_db_path = "chroma_db"  # Đường dẫn database Chroma
# vector_db = Chroma.from_documents(split_docs, embedding_model, persist_directory=chroma_db_path)
# vector_db.persist()
# print("Đã lưu embeddings vào ChromaDB!")

#Lưu vector vào database MilvusDB
#Tạo connection đến Milvus
try:
    connections.connect(
        alias="default",
        host="localhost",  # Thay bằng IP server nếu cần
        port="19530"
    )
    print("Kết nối Milvus thành công!")
    vectorstore = Milvus(
        embedding_function=embedding_model,
        connection_args={"uri":"http://localhost:19530"},
        collection_name="TestDB",
        drop_old=True  # Xóa data đã tồn tại trong collection
    )
    doc_ids = [str(uuid.uuid4()) for _ in split_docs]
    vectorstore.add_documents(split_docs, ids = doc_ids)  # Thêm documents vào Milvus
    print("Đã lưu embeddings vào MilvusDB!")
except Exception as e:
    print(f"Kết nối Milvus thất bại: {e}")

# use api Nvidia
