import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import ChatApp from "./pages/ChatApp.jsx";
import HomePage from "./pages/HomePage.jsx";
import Signup from "./pages/Signup.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />}>
        <Route index element={<Login />} />
      </Route>
      <Route path="/chatapp" element={<ChatApp />} />
      <Route path="/Signup" element={<Signup />} />
    </Routes>
  );
}

export default App;
