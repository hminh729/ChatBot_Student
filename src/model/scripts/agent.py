# Import các thư viện cần thiết từ LangChain và các thư viện liên quan
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import Milvus  # type: ignore
from langchain_community.embeddings import OllamaEmbeddings  # type: ignore
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever  # type: ignore
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import os
import getpass

# Hàm khởi tạo retriever bằng cách kết hợp Milvus + BM25
def get_retriever(collection_name: str) -> EnsembleRetriever:
    try:
        # Khởi tạo mô hình embedding từ Ollama với model bge-m3
        embedding_model = OllamaEmbeddings(
            model="bge-m3:567m",
            base_url="http://ollama:11434"
        )

        # Kết nối tới Milvus vectorstore
        vectorstore = Milvus(
            embedding_function=embedding_model,
            collection_name=collection_name,
            connection_args={"host": "milvus-standalone", "port": "19530"}
        )

        # Tạo retriever từ Milvus với truy vấn tương tự (similarity search)
        milvus_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )

        # Truy vấn Milvus để lấy 100 documents gần nhất, dùng cho BM25 retriever
        documents = [
            Document(page_content=doc.page_content, metadata=doc.metadata)
            for doc in vectorstore.similarity_search("", k=100)
        ]

        # Kiểm tra nếu không có documents thì raise lỗi
        if not documents:
            raise ValueError(f"Không tìm thấy documents trong collection '{collection_name}'")

        # Khởi tạo BM25 retriever từ các documents đã lấy
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 4

        # Kết hợp hai retriever bằng EnsembleRetriever với trọng số 70-30
        ensemble_retriever = EnsembleRetriever(
            retrievers=[milvus_retriever, bm25_retriever],
            weights=[0.7, 0.3]
        )

        return ensemble_retriever

    except Exception as e:
        print(f"Lỗi khi khởi tạo retriever: {str(e)}")

        # Nếu xảy ra lỗi, trả về retriever mặc định với document thông báo lỗi
        default_doc = [
            Document(
                page_content="Có lỗi xảy ra khi kết nối database. Vui lòng thử lại sau.",
                metadata={"source": "error"}
            )
        ]
        return BM25Retriever.from_documents(default_doc)

# Hàm khởi tạo LLM và Agent có khả năng gọi tool
def get_llm_and_agent(retriever):
    # Khởi tạo tool tìm kiếm tài liệu dựa trên retriever
    find_documents_tool = create_retriever_tool(
        retriever,
        "find_documents",
        "Search for information of lịch sử đảng."
    )

    # Kiểm tra và lấy API key của Cohere nếu chưa có trong biến môi trường
    if not os.environ.get("COHERE_API_KEY"):
        os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")

    # Khởi tạo mô hình LLM từ Cohere với temperature = 0.5
    llm = init_chat_model(
        "command-r-plus",
        model_provider="cohere",
        model_kwargs={"temperature": 0.5}
    )

    # Khai báo danh sách tool sử dụng trong agent
    tools = [find_documents_tool]

    # Prompt hệ thống để kiểm soát hành vi của agent
    system = """Bạn là trợ lý thông minh. 
Chỉ trả lời câu hỏi nếu bạn tìm thấy thông tin từ giáo trình được cung cấp.
Nếu không tìm thấy, hãy trả lời: "Xin lỗi, tôi không tìm thấy thông tin trong giáo trình."""
    
    # Cấu trúc prompt với hệ thống, lịch sử hội thoại, input người dùng và agent_scratchpad
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Tạo agent với khả năng gọi tool
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    # Trả về executor để chạy agent cùng với tool, bật chế độ verbose để dễ debug
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
