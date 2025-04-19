import React from "react";
import axios from "axios";

const HomePage = () => {
  const [fullName, setFullName] = React.useState("");
  const [userId, setUserId] = React.useState("");
  const [fbLink, setFbLink] = React.useState("");
  const url = "http://localhost:8000/signup/";
  const handleSubmit = async () => {
    await axios.post(url, {
      fullName,
      userId,
      fbLink,
    });
    console.log("hi");
  };
  return (
    <>
      <div className="gap-4 flex justify-center ">
        <input
          type="text"
          placeholder="Enter your full name..."
          className="border"
          onChange={(e) => setFullName(e.target.value)}
        />
        <input
          type="text "
          placeholder="Enter your Student ID..."
          className="border"
          onChange={(e) => setUserId(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter your link Facebook..."
          className="border"
          onChange={(e) => setFbLink(e.target.value)}
        />
      </div>
      <div className="flex justify-center mt-2">
        <button className="border cursor-pointer" onClick={handleSubmit}>
          Submit
        </button>
      </div>
    </>
  );
};

export default HomePage;
