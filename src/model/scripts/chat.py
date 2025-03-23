import ollama
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# 🛠️ Load database từ Chroma
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")
vector_db = Chroma(persist_directory="db", embedding_function=embedding_model)

# 🔥 Hàm hỏi đáp với chatbot
def ask_bot(query):
    # 🔍 Tìm kiếm nội dung liên quan trong ChromaDB
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])

    # 🎯 Tạo prompt với dữ liệu từ giáo trình
    prompt = f"Thông tin từ giáo trình:\n{context}\n\nCâu hỏi: {query}\nTrả lời chi tiết:"
    
    # 🧠 Gửi vào DeepSeek (hoặc bất kỳ model nào trong Ollama)
    response = ollama.chat(model="deepseek", messages=[{"role": "user", "content": prompt}])
    
    return response["message"]["content"]

# 💬 Chạy chatbot trong terminal
while True:
    user_input = input("Bạn: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    print("AI:", ask_bot(user_input))
