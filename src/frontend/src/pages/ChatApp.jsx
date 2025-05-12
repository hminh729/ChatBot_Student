import React, { useState } from "react";
import ChatBox from ".././Component/ChatBox.jsx";
import ChatHeader from ".././Component/ChatHeader.jsx";
import Sidebar from ".././Component/SideBar.jsx";

const App = () => {
  const [modelChoice, setModelChoice] = useState("OpenAI GPT-4");
  const [collectionName, setCollectionName] = useState("data_test");
  const stu_id = "B22DCCN542";
  const subject_name = "lichsudang";

  return (
    <div className="flex h-screen">
      <Sidebar
        setModelChoice={setModelChoice}
        setCollectionName={setCollectionName}
      />
      <div className="flex-grow p-4">
        <ChatHeader modelChoice={modelChoice} />
        <ChatBox
          modelChoice={modelChoice}
          collectionName={collectionName}
          stu_id={stu_id}
          subject_name={subject_name}
        />
      </div>
    </div>
  );
};

export default App;
