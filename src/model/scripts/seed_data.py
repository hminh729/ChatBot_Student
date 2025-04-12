import getpass
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from mistralai import Mistral
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from uuid import uuid4
from pymilvus.model.dense import MistralAIEmbeddingFunction
from langchain_cohere import CohereEmbeddings


import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Chọn model để tạo embeddings
use_model = "bge-m3:567m"  # Chọn "mistral" hoặc "bge-m3:567m"

# Kết nối với Milvus
connections.connect(host="localhost", port="19530")

# Định nghĩa đường dẫn file PDF
file_path = "../data/BAI-GIANG-LSĐ-2021.pdf"
loader = PyPDFLoader(file_path, extract_images=True)
documents = loader.load()

# Chia nhỏ văn bản thành các đoạn nhỏ (chunks)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=70)
chunks = text_splitter.split_documents(documents)

# Tạo embeddings từ model đã chọn
def mistral_embeddings(chunks):
    api_key = os.getenv("MISTRAL_API_KEY")
    model = "mistral-embed"
    client = Mistral(api_key=api_key)
    inputs = [chunk.page_content for chunk in chunks]
    embeddings_batch_response = client.embeddings.create(model=model, inputs=inputs)
    embeddings = [data.embedding for data in embeddings_batch_response.data]
    return embeddings
if use_model == "mistral":
    print("")
elif use_model == "bge-m3:567m":
    embeddings = OllamaEmbeddings(model=use_model)
elif use_model == "cohere":
    if not os.environ.get("COHERE_API_KEY"):
        os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
    embeddings = CohereEmbeddings(model="embed-english-v3.0")
else:
    raise ValueError("Model không hợp lệ. Chọn 'mistral' hoặc 'bge-m3'")

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

# Tạo danh sách UUID cho từng document
uuids = [str(uuid4()) for _ in range(len(documents))]


if use_model == "bge-m3:567m":
    try:
        connections.connect(
            alias="default",
            host="localhost",  # Thay bằng IP server nếu cần
            port="19530"
        )
        print("Kết nối Milvus thành công!")
        vectorstore = Milvus(
            embedding_function=embeddings,
            connection_args={"uri":"http://localhost:19530"},
            collection_name="TestDB",
            drop_old=True  # Xóa data đã tồn tại trong collection
        )
        vectorstore.add_documents(documents=documents, ids = uuids)  # Thêm documents vào Milvus
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")

elif use_model == "mistral":

    try:
        connections.connect(
            host="localhost",  # Thay bằng IP server nếu cần
            port="19530"
        )
        print("Kết nối Milvus thành công!")
        vectorstore = Milvus(
            embedding_function=mistral_embeddings(chunks),
            connection_args={"uri":"http://localhost:19530"},
            collection_name="TestDB",
            drop_old=True  # Xóa data đã tồn tại trong collection
        )
        inputs = [doc.page_content for doc in documents]

        # docs_embeddings = embeddings.encode_documents(inputs)
        # print(type(docs_embeddings[0]))  # Phải là <class 'list'> hoặc <class 'np.ndarray'>
        # print(len(docs_embeddings), len(docs_embeddings[0])) 
        vectorstore.add_documents(documents=documents,ids=uuids) # Thêm documents vào Milvus
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Erorr is: {e}")

elif use_model == "cohere":
    try:
        connections.connect(
            alias="default",
            host="localhost",  # Thay bằng IP server nếu cần
            port="19530"
        )
        print("Kết nối Milvus thành công!")
        vectorstore = Milvus(
            embedding_function=embeddings,
            connection_args={"uri":"http://localhost:19530"},
            collection_name="TestDB",
            drop_old=True  # Xóa data đã tồn tại trong collection
        )
        vectorstore.add_documents(documents=documents, ids = uuids)  # Thêm documents vào Milvus
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")