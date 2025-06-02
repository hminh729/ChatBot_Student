ChatBot Hỗ trợ hỏi đáp cho sinh viên

Hướng dẫn chạy dự án trên window

Bước 1: Cài đặt các công cụ cần thiết
Docker-destop và wsl( Windows Subsystem for Linux)
Bước 2.Build dự án frontend
Bước đầu di chuyển vào thư mục frontend:
cd src/frontend
Chạy lệnh sau để build dự án frontend
npm run build
Bước 3.Build dự án(cần bật docker destop trước)
Tiếp theo cd ra thư mục gốc:
cd ..
Di chuyển vào thư mục production:
cd production
Chạy lệnh sau để build dự án
docker compose -p chatbot up -d
Khi build xong, tiến hành pull mô hình bge-m3:567m :
Di chuyển vào container ollama:
docker exec -it chatbot-ollama-1 /bin/bash
Chạy lênh sau để pull model:
ollama pull bge-m3:567m
Dừng docker và khởi động lại container
docker stop chatbot
docker start chatbot

Em vừa test lại thì gặp 1 bug là khi em upload file pdf thì xảy ra lỗi là frontend hiển thị upload thất bại, nhưng em đợi thêm khoảng 5' cho model embedding xong dữ liệu vào milvus thì lại thành công.Nên khi thầy test thì mong thầy chịu khó đợi 1 chút ạ.
