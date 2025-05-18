import getpass
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from mistralai import Mistral
from pymilvus import connections, utility
from uuid import uuid4
from langchain_cohere import CohereEmbeddings
import os
from dotenv import load_dotenv


# Load biến môi trường
load_dotenv()
def connect_milvus():
    connections.connect(
            alias="default",
            host="localhost",  # Thay bằng IP server nếu cần
            port="19530"
        )
    print("Kết nối Milvus thành công!")
# Hàm này để load file pdf từ thư mục data
def load_file_pdf(file_path:str):
    """
    Hàm này dùng để load file pdf từ đường dẫn file_path
    """
    loader = PyPDFLoader(file_path, extract_images=True)
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
    embeddings = OllamaEmbeddings(model=use_model)
    try:
        
        vectorstore = Milvus(
            embedding_function=embeddings,
            connection_args={"uri":url},
            collection_name=collection_name,
            drop_old=False  # Xóa data đã tồn tại trong collection
        )
        vectorstore.add_documents(documents=documents, ids = uuids)  # Thêm documents vào Milvus
        print("Đã lưu embeddings vào MilvusDB!")
    except Exception as e:
        print(f"Kết nối Milvus thất bại: {e}")

def delete_collection(collection_name:str):
    connect_milvus()
    utility.drop_collection(collection_name)
    print(f"Đã xóa collection {collection_name} thành công!")
        
# seed_data_milvus_ollama(
#     file_path="../data/1.pdf",
#     use_model="bge-m3:567m",   # Thay model tùy bạn chọn
#     collection_name="TestDB",
#     url="http://localhost:19530"
# )

# Chọn model để tạo embeddings
#  "bge-m3:567m"  # Chọn "mistral" hoặc "bge-m3:567m"







# # Tạo embeddings từ model đã chọn
# def mistral_embeddings(chunks):
#     api_key = os.getenv("MISTRAL_API_KEY")
#     model = "mistral-embed"
#     client = Mistral(api_key=api_key)
#     inputs = [chunk.page_content for chunk in chunks]
#     embeddings_batch_response = client.embeddings.create(model=model, inputs=inputs)
#     embeddings = [data.embedding for data in embeddings_batch_response.data]
#     return embeddings
# if use_model == "mistral":
#     print("")
# elif use_model == "bge-m3:567m":
    
# elif use_model == "cohere":
#     if not os.environ.get("COHERE_API_KEY"):
#         os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
#     embeddings = CohereEmbeddings(model="embed-english-v3.0")
# else:
#     raise ValueError("Model không hợp lệ. Chọn 'mistral' hoặc 'bge-m3'")



# # Tạo danh sách UUID cho từng document



# if use_model == "bge-m3:567m":
    

# elif use_model == "mistral":

#     try:
#         connections.connect(
#             host="localhost",  # Thay bằng IP server nếu cần
#             port="19530"
#         )
#         print("Kết nối Milvus thành công!")
#         vectorstore = Milvus(
#             embedding_function=mistral_embeddings(chunks),
#             connection_args={"uri":"http://localhost:19530"},
#             collection_name="TestDB",
#             drop_old=True  # Xóa data đã tồn tại trong collection
#         )
#         inputs = [doc.page_content for doc in documents]

#         # docs_embeddings = embeddings.encode_documents(inputs)
#         # print(type(docs_embeddings[0]))  # Phải là <class 'list'> hoặc <class 'np.ndarray'>
#         # print(len(docs_embeddings), len(docs_embeddings[0])) 
#         vectorstore.add_documents(documents=documents,ids=uuids) # Thêm documents vào Milvus
#         print("Đã lưu embeddings vào MilvusDB!")
#     except Exception as e:
#         print(f"Erorr is: {e}")

# elif use_model == "cohere":
    # try:
    #     connections.connect(
    #         alias="default",
    #         host="localhost",  # Thay bằng IP server nếu cần
    #         port="19530"
    #     )
    #     print("Kết nối Milvus thành công!")
    #     vectorstore = Milvus(
    #         embedding_function=embeddings,
    #         connection_args={"uri":"http://localhost:19530"},
    #         collection_name="TestDB",
    #         drop_old=True  # Xóa data đã tồn tại trong collection
    #     )
    #     vectorstore.add_documents(documents=documents, ids = uuids)  # Thêm documents vào Milvus
    #     print("Đã lưu embeddings vào MilvusDB!")
    # except Exception as e:
    #     print(f"Kết nối Milvus thất bại: {e}")