import React from "react";
import { BrowserRouter, Routes, Route } from "react-router";
import Login from "./pages/Login.jsx";
import ChatApp from "./pages/ChatApp.jsx";
import Signup from "./pages/Signup.jsx";

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Signup />} />
        <Route path="/chatapp" element={<ChatApp />} />
      </Routes>
    </div>
  );
};

export default App;
