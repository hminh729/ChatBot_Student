import ChatBox from "../Component/ChatBox.jsx";
import ChatHeader from "../Component/ChatHeader.jsx";
import Sidebar from "../Component/Sidebar.jsx";
import { useState } from "react";

const App = () => {
  const stu_id = localStorage.getItem("stu_id");
  const [subject_name, setSubject_name] = useState("");

  return (
    <div className="flex h-screen">
      <Sidebar stu_id={stu_id} onSetSubject_name={setSubject_name} />
      <div className="flex-grow p-4">
        <ChatHeader />
        <ChatBox stu_id={stu_id} subject_name={subject_name} />
      </div>
    </div>
  );
};

export default App;
