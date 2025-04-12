from langchain.tools.retriever import create_retriever_tool
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import Milvus # type: ignore
from langchain_community.embeddings import OllamaEmbeddings # type: ignore
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever # type: ignore
from langchain_core.documents import Document
import os
from langchain.chat_models import init_chat_model
from mistralai import Mistral # type: ignore
import getpass

def get_retriever(collection_name: str = "TestDB") -> EnsembleRetriever:
    try:
        # Embedding + Milvus
        embedding_model = OllamaEmbeddings(model="bge-m3:567m")
        vectorstore = Milvus(
            embedding_function=embedding_model,
            connection_args={"host": "localhost", "port": "19530"},
            collection_name=collection_name,
        )

        # Milvus retriever
        milvus_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        # Lấy tất cả documents từ vectorstore
        documents = [
            Document(page_content=doc.page_content, metadata=doc.metadata)
            for doc in vectorstore.similarity_search("", k=100)
        ]
        if not documents:
            raise ValueError(f"Không tìm thấy documents trong collection '{collection_name}'")
        # BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 4
    
        # Ensemble retriever
        ensemble_retriever = EnsembleRetriever(
            retrievers=[milvus_retriever, bm25_retriever],
            weights=[0.7, 0.3]
        )
        return ensemble_retriever

    except Exception as e:
        print(f"Lỗi khi khởi tạo retriever: {str(e)}")
        # Trả về retriever default
        default_doc = [
            Document(
                page_content="Có lỗi xảy ra khi kết nối database. Vui lòng thử lại sau.",
                metadata={"source": "error"}
            )
        ]
        return BM25Retriever.from_documents(default_doc)

# Khởi tạo retriever tool
tool = create_retriever_tool(
    get_retriever(),
    "find_documents",
    "Search for information of lịch sử đảng."
)

def get_llm_and_agent(retriever):
    """
    Khởi tạo LLM và agent với Ollama.
    """
    
    # Khởi tạo ChatOllama
    # llm = ChatOllama(
    #     model="mistral:latest",
    #     temperature=0,
    #     streaming=True
    # )

    #Khởi tạo chatbot Mistral
    # if not os.environ.get("MISTRAL_API_KEY"):
    #     os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter API key for Mistral AI: ")
    # llm = init_chat_model("mistral-large-latest", model_provider="mistralai")

    # Khởi tạo chatbot Cohere
    if not os.environ.get("COHERE_API_KEY"):
        os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
    
    llm = init_chat_model("command-r-plus", model_provider="cohere", model_kwargs={"temperature": 0})
    tools = [tool]

    # Thiết lập prompt template
    system = """Bạn là trợ lý thông minh. 
Chỉ trả lời câu hỏi nếu bạn tìm thấy thông tin từ giáo trình được cung cấp.
Nếu không tìm thấy, hãy trả lời: "Xin lỗi, tôi không tìm thấy thông tin trong giáo trình."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Tạo agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

retriever = get_retriever()
agent_executor = get_llm_and_agent(retriever)

# Chạy chatbot
while True:
    user_input = input("Bạn: ")
    if user_input.lower() in ["exit", "quit", "thoát"]:
        print("Đã thoát khỏi chatbot!")#      
        break  # Thoát vòng lặp nếu người dùng nhập exit
    response = agent_executor.invoke({
        "input": user_input
    })
    print("Agent:", response["output"]) 
