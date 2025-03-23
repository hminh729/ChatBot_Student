import ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Kết nối với ChromaDB
def load_vector_db(db_path="db"):
    embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
    return Chroma(persist_directory=db_path, embedding_function=embedding_model)

def retrieve_context(vector_db, query):
    """Truy vấn dữ liệu từ ChromaDB để lấy thông tin liên quan"""
    results = vector_db.similarity_search(query, k=3)  # Lấy 3 kết quả gần nhất
    context = "\n".join([doc.page_content for doc in results])
    return context if context else "Không tìm thấy dữ liệu liên quan."

def chat_with_ollama(model="deepseek-r1:1.5b ", db_path="db"):
    print("🤖 AI Chatbot với ChromaDB (Nhập 'exit' để dừng)\n")

    vector_db = load_vector_db(db_path)  # Load database

    while True:
        user_input = input("Bạn: ")

        if user_input.lower() == "exit":
            print("👋 Tạm biệt!")
            break  # Dừng chat

        # Truy xuất dữ liệu từ ChromaDB
        context = retrieve_context(vector_db, user_input)

        # Gửi tin nhắn đến Ollama với dữ liệu từ ChromaDB
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "Bạn là một trợ lý AI thông minh, hãy trả lời chính xác."},
                {"role": "user", "content": f"Câu hỏi: {user_input}\nDữ liệu liên quan:\n{context}"}
            ]
        )

        print(f"AI: {response['message']['content']}\n")

if __name__ == "__main__":
    chat_with_ollama(model="gemma3:1b", db_path="db")
