import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
const Login = () => {
  const [stu_id, setStu_id] = useState("");
  const [password, setPassword] = useState("");
  const nagivate = useNavigate();
  const handleClick = async () => {
    try {
      if (stu_id === "" || password === "") {
        alert("Vui lòng nhập đầy đủ thông tin.");
        return;
      }
      const res = await axios.post(
        `http://localhost:8000/login/${stu_id}/${password}`
      );
      if (res.data.status === "success") {
        localStorage.setItem("stu_id", stu_id);
        nagivate("/chatapp");
      } else {
        alert("Sai thông tin đăng nhập.");
      }
    } catch (error) {
      console.error(error);
      alert("Lỗi kết nối đến máy chủ.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold text-center text-gray-700 mb-6">
          Đăng nhập
        </h2>
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Mã sinh viên
          </label>
          <input
            type="text"
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Nhập mã sinh viên"
            value={stu_id}
            onChange={(e) => setStu_id(e.target.value)}
          />
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-600 mb-1">
            Mật khẩu
          </label>
          <input
            type="password"
            className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Nhập mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="flex justify-between gap-4 mt-4">
          <button
            type="submit"
            onClick={handleClick}
            className="w-1/2 bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-200"
          >
            Đăng Nhập
          </button>
          <Link to="/signUp" className="w-1/2">
            <button
              type="button"
              className="w-full bg-gray-300 text-gray-800 py-2 rounded-md hover:bg-gray-400 transition duration-200"
            >
              Đăng Ký
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
