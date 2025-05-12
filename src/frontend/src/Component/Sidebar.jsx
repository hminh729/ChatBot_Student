import React, { useState } from "react";
import axios from "axios";

const Sidebar = ({ setModelChoice, setCollectionName }) => {
  const [model, setModel] = useState("OpenAI GPT-4");
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [subject_name, setSuject_name] = useState("");

  const handleModelChange = (e) => {
    const model = e.target.value;
    setModel(model);
    setModelChoice(model);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadStatus("⚠️ Chưa chọn file");
      return;
    }

    try {
      setIsUploading(true); // Start loading
      setUploadStatus(""); // Reset status
      const arr = subject_name.split(" ");
      const subject_id = arr.map((arr) => arr[0]).join("");
      const stu_id = "B22DCCN542";
      await axios.post(`http://127.0.0.1:8000/add_subject/${stu_id}`, {
        subject_id,
        subject_name,
      });
      const formData = new FormData();
      formData.append("file", file);
      formData.append("subject_name", subject_name);
      const res = await axios.post(
        "http://127.0.0.1:8000/post_file",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      setUploadStatus("✅ Upload thành công!");
      setFile(null);
    } catch (error) {
      console.error(error);
      setUploadStatus("❌ Upload thất bại.");
    } finally {
      setIsUploading(false); // End loading
    }
  };

  return (
    <div className="w-64 p-4 bg-gray-200">
      <h3 className="mt-4">Embeddings Model</h3>
      <select
        className="w-full p-2 mt-2 border border-gray-300 rounded"
        onChange={handleModelChange}
      >
        <option value="Ollama (Local)">Ollama (Local)</option>
        <option value="OpenAI GPT-4">OpenAI GPT-4</option>
        <option value="OpenAI Grok">OpenAI Grok</option>
      </select>

      <input
        type="text"
        placeholder="Subject Name"
        value={subject_name}
        onChange={(e) => setSuject_name(e.target.value)}
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
        disabled={isUploading} // Disable while uploading
      >
        {isUploading ? "⏳ Đang upload..." : "Upload"}
      </button>

      {uploadStatus && <p className="mt-2 text-sm">{uploadStatus}</p>}
    </div>
  );
};

export default Sidebar;
