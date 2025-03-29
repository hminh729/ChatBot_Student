from langchain.tools.retriever import create_retriever_tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import OllamaEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

def get_retriever(collection_name: str = "TestDB") -> EnsembleRetriever:
    """
    Tạo một ensemble retriever kết hợp vector search (Milvus) và BM25.
    """
    try:
        # Kết nối với Milvus và tạo vector retriever
        embedding_model = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Milvus(
            embedding_function=embedding_model,
            connection_args={"uri": "http://localhost:19530"},
            collection_name=collection_name,
        )
        milvus_retriever = vectorstore.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )

        # Tạo BM25 retriever từ toàn bộ documents
        try:
            all_documents = vectorstore.similarity_search("sample query", k=100)
            documents = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in all_documents]
            if not documents:
                raise ValueError("Không tìm thấy dữ liệu trong Milvus.")
        except Exception as e:
            print(f"Lỗi khi truy vấn Milvus: {e}")
            documents = []

        if not documents:
            raise ValueError(f"Không tìm thấy documents trong collection '{collection_name}'")

        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 4

        # Kết hợp hai retriever với tỷ trọng
        ensemble_retriever = EnsembleRetriever(
            retrievers=[milvus_retriever, bm25_retriever],
            weights=[0.7, 0.3]
        )
        return ensemble_retriever

    except Exception as e:
        print(f"Lỗi khi khởi tạo retriever: {str(e)}")
        # Trả về retriever với document mặc định nếu có lỗi
        default_doc = [
            Document(
                page_content="Có lỗi xảy ra khi kết nối database. Vui lòng thử lại sau.",
                metadata={"source": "error"}
            )
        ]
        return BM25Retriever.from_documents(default_doc)

def get_llm_and_agent(retriever):
    """
    Khởi tạo LLM và agent với Ollama.
    """
    # Tạo retriever tool
    tool = create_retriever_tool(
        retriever,
        "find_documents",
        "Search for information of lịch sử đảng."
    )

    # Khởi tạo ChatOllama
    llm = ChatOllama(
        model="llama2:7b",  # Xóa khoảng trắng dư
        temperature=0,
        streaming=True
    )

    tools = [tool]

    # Thiết lập prompt template
    system = """You are an expert at AI. Your name is ChatchatAI. For all questions call the find_documents tool"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Tạo agent
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

retriever = get_retriever()
agent_executor = get_llm_and_agent(retriever)

# Chạy chatbot
while True:
    user_input = input("Bạn: ")
    if user_input.lower() in ["exit", "quit", "thoát"]:
        print("Đã thoát khỏi chatbot!")
        break  # Thoát vòng lặp nếu người dùng nhập exit
    
    response = agent_executor.invoke({"input": user_input})
    print("Agent:", response["output"])  # In câu trả lời từ agent
