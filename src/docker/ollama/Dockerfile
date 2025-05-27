FROM ollama/ollama

# Cài thêm curl để kiểm tra trạng thái
RUN apt-get update && apt-get install -y curl

COPY pull-model.sh /pull-model.sh
RUN chmod +x /pull-model.sh

# Khi container khởi động thì chạy pull model trước
ENTRYPOINT ["/pull-model.sh"]
