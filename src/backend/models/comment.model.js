import mongoose from "mongoose";
import Schema from "mongoose";

const CommentSchema = new Schema(
  {
    blog_id: {
      type: [Schema.Types.ObjectId],
      ref: "Blog",
      require: true,
    },
    blog_author: {
      type: [Schema.Types.ObjectId],
      ref: "User",
      require: true,
    },
    parent_comment: {
      type: [Schema.Types.ObjectId],
      ref: "Comment",
    },
    child_comment: {
      type: [Schema.Types.ObjectId],
      ref: "Comment",
    },
    commented_by: {
      type: [Schema.Types.ObjectId],
      ref: "User",
      require: true,
    },
    is_reply: {
      type: Boolean,
      default: false,
    },
    comment: {
      type: String,
      required: true,
    },
  },
  {
    timestamps: {
      createdAt: "created_at",
    },
  }
);

const Comment = mongoose.model("Comment", CommentSchema);
export default Comment;
