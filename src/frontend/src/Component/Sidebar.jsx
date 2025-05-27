import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router";
import { MdDelete } from "react-icons/md";

const Sidebar = ({ stu_id, onSetSubject_name }) => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [subject_name, setSubject_name] = useState("");
  const [subjects, setSubjects] = useState([]);
  const navigate = useNavigate();
  const getSubjects = async () => {
    try {
      const res = await axios.get(`api/get_subjects/${stu_id}`);
      setSubjects(res.data.subjects);
    } catch (error) {
      console.error("Lỗi khi tải danh sách môn học:", error);
    }
  };
  useEffect(() => {
    getSubjects();
  }, [stu_id]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file || !subject_name) {
      setUploadStatus("⚠️ Vui lòng chọn file và nhập tên môn học.");
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus("");

      const arr = subject_name.trim().split(" ");
      const subject_id = arr.map((word) => word[0]).join("");

      // Gửi môn học mới
      await axios.post(`api/add_subject/${stu_id}`, {
        subject_id,
        subject_name,
      });

      // Upload file
      const formData = new FormData();
      formData.append("file", file);
      formData.append("subject_name", subject_name);
      formData.append("stu_id", stu_id);
      await axios.post("api/post_file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadStatus("✅ Upload thành công!");
      setFile(null);
      setSubject_name("");

      // Cập nhật lại danh sách môn học
      getSubjects();
    } catch (error) {
      console.error("Lỗi khi upload:", error);
      setUploadStatus("❌ Upload thất bại.");
    } finally {
      setIsUploading(false);
    }
  };
  const handleLogout = () => {
    localStorage.removeItem("stu_id");
    navigate("/");
  };
  const handleDelete = async (subject_name) => {
    try {
      const res = await axios.post(
        `api/delete_subject/${stu_id}/${subject_name}`
      );
      if (res.status === 200) {
        alert("Xóa môn học thành công");
        getSubjects();
      } else {
        setUploadStatus("❌ Xóa môn học thất bại.");
      }
    } catch (error) {}
  };

  return (
    <div className="w-64 p-4 bg-gray-200 min-h-screen">
      <h3 className="text-lg font-semibold mb-2">Upload tài liệu</h3>
      <button onClick={handleLogout} className="bg-gray-300 cursor-pointer">
        Logout
      </button>

      <input
        type="text"
        placeholder="Tên môn(viết liền không dấu)"
        value={subject_name}
        onChange={(e) => setSubject_name(e.target.value)}
        className="w-full p-2 mt-2 border border-gray-300 rounded"
      />

      <input
        type="file"
        accept="application/pdf"
        className="w-full p-2 mt-2 border border-gray-300 rounded"
        onChange={handleFileChange}
      />

      <button
        className="mt-2 w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
        onClick={handleUpload}
        disabled={isUploading}
      >
        {isUploading ? "⏳ Đang upload..." : "Upload"}
      </button>

      {uploadStatus && <p className="mt-2 text-sm">{uploadStatus}</p>}

      <div className="mt-6">
        <h4 className="text-md font-semibold mb-2">Danh sách môn học:</h4>
        {subjects.length > 0 ? (
          subjects.map((subject, index) => (
            <div className="flex items-center justify-between ">
              <div
                key={index}
                className="p-2 bg-blue-400 cursor-pointer rounded mb-2 shadow-sm hover:bg-blue-500"
                onClick={() => onSetSubject_name(subject)}
              >
                <p>{subject}</p>
              </div>
              <div>
                <MdDelete
                  className="size-7 cursor-pointer"
                  onClick={() => handleDelete(subject)}
                />
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-600">Chưa có môn học nào.</p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
