import mongoose from "mongoose";
const { Schema } = mongoose;

// Định nghĩa schema cho một tin nhắn trong lịch sử
const ChatMessageSchema = new Schema({
  role: {
    type: String,
    enum: ["user", "bot"],
    required: true,
  },
  content: {
    type: String,
    required: true,
  },
  timestamp: {
    type: Date,
    default: Date.now,
  },
});

// Định nghĩa schema cho một môn học
const SubjectSchema = new Schema({
  idSubject: {
    type: String,
    required: true,
  },
  nameSubject: {
    type: String,
    required: true,
  },
  history: {
    type: [ChatMessageSchema],
    default: [],
  },
});

// Schema chính cho người dùng
const UserSchema = new Schema(
  {
    fullname: {
      type: String,
      required: true,
    },
    idStudent: {
      type: String,
      required: true,
    },
    idFB: {
      type: String,
      required: true,
      unique: true,
    },
    currentSubjectId: {
      type: String,
      default: null,
    },
    subjects: {
      type: [SubjectSchema],
      default: [],
    },
  },
  {
    timestamps: true,
  }
);

const User = mongoose.model("User", UserSchema);
export default User;
