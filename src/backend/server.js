import express from "express";
import dotenv from "dotenv";
import cookieParser from "cookie-parser";

import connectDB from "./config/db.js";
import authRoutes from "./routes/authroutes.js";
import blogRoutes from "./routes/blogRoutes.js";
dotenv.config();

const Post = process.env.PORT;

const app = express();

app.use(express.json());
app.use(cookieParser());

app.use("/api/v1/auth", authRoutes);
app.use("/api/v1/blog", blogRoutes);

app.listen(Post, () => {
  connectDB();
  console.log(`Server started on http://localhost:${Post}`);
});
