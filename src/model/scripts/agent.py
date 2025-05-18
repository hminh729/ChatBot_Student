from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import Milvus # type: ignore
from langchain_community.embeddings import OllamaEmbeddings # type: ignore
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever # type: ignore
from langchain_core.documents import Document
import os
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
import getpass
import nest_asyncio


nest_asyncio.apply()
def get_retriever(collection_name: str) -> EnsembleRetriever:
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
            weights=[0.6, 0.4]
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



@tool
def summarize_section_tool(topic: str) -> str:
    """
    Tổng hợp nội dung liên quan đến một chủ đề trong giáo trình.
    Nhập vào tên chương hoặc từ khóa (ví dụ: 'Chương 1', 'Tư tưởng Hồ Chí Minh').
    Trả về bản tóm tắt nội dung từ giáo trình.
    """
    try:
        # Lấy retriever
        retriever = get_retriever()

        # Truy vấn tìm đoạn văn bản liên quan
        docs = retriever.get_relevant_documents(topic)
        if not docs:
            return "Không tìm thấy nội dung liên quan trong giáo trình."

        # Gộp nội dung lại
        full_text = "\n\n".join(doc.page_content for doc in docs)

        # Gửi cho LLM để tóm tắt
        if not os.environ.get("COHERE_API_KEY"):
            os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
        llm = init_chat_model("command-r-plus", model_provider="cohere", model_kwargs={"temperature": 0})
        prompt = f"Tóm tắt nội dung sau đây liên quan đến '{topic}':\n\n{full_text}"
        summary = llm.invoke(prompt)

        return summary.content if hasattr(summary, "content") else summary

    except Exception as e:
        return f"Có lỗi xảy ra: {str(e)}"


def get_llm_and_agent(retriever):
    # Khởi tạo retriever tool
    find_documents_tool = create_retriever_tool(
        retriever,
        "find_documents",
        "Search for information of lịch sử đảng."
    )
   
    # Khởi tạo chatbot Cohere
    if not os.environ.get("COHERE_API_KEY"):
        os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
    
    llm = init_chat_model("command-r-plus", model_provider="cohere", model_kwargs={"temperature": 0.5})
    tools = [find_documents_tool]

    system = """Bạn là trợ lý thông minh. 
Chỉ trả lời câu hỏi nếu bạn tìm thấy thông tin từ giáo trình được cung cấp.
Nếu không tìm thấy, hãy trả lời: "Xin lỗi, tôi không tìm thấy thông tin trong giáo trình."""
    prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    MessagesPlaceholder(variable_name="chat_history"),       
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"), 
])

    # Tạo agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
