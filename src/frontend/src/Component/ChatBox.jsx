import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

const ChatBox = ({ stu_id, subject_name }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await axios.get(
          `http://127.0.0.1:8000/get_message/${stu_id}/${subject_name}`
        );
        setMessages(res.data.messages);
      } catch (error) {
        console.error("Lỗi khi tải tin nhắn:", error);
      }
    };

    fetchMessages();
  }, [stu_id, subject_name]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInputChange = (e) => setInput(e.target.value);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    const formData = new FormData();
    formData.append("input", input);
    setInput("");
    try {
      const res = await axios.post(
        `http://127.0.0.1:8000/get_response/${stu_id}/${subject_name}`,
        formData,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      const botMessage = {
        role: "assistant",
        content: res.data.message,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Lỗi khi gửi tin nhắn:", error);
    } finally {
      setInput("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSendMessage();
  };

  return (
    <div className="flex flex-col h-[80vh] max-h-[80vh] p-4 border rounded shadow">
      {/* Vùng hiển thị tin nhắn */}
      <div className="flex-1 overflow-y-auto p-2 bg-gray-50 rounded">
        {messages &&
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`my-1 flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-2 max-w-xs rounded-lg ${
                  msg.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Khung nhập tin nhắn */}
      <div className="mt-4 flex space-x-2">
        <input
          type="text"
          className="flex-grow p-2 border border-gray-300 rounded"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Hãy hỏi tôi bất cứ điều gì..."
        />
        <button
          className="p-2 bg-green-500 text-white rounded"
          onClick={handleSendMessage}
        >
          Gửi
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
