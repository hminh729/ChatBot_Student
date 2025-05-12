import React from "react";

const ChatHeader = ({ modelChoice }) => {
  return (
    <header className="p-4 bg-blue-500 text-white">
      <h1 className="text-2xl">💬 AI Assistant</h1>
      <p className="mt-2 text-lg">
        Người bạn đồng hành của bạn trong việc học tập và nghiên cứu.
      </p>
    </header>
  );
};

export default ChatHeader;
