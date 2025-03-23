import mongoose from "mongoose";
import Schema from "mongoose";
const BlogSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: true,
    },
    content: {
      type: String,
      // required:true
    },
    banner_image: {
      type: String,
      // required:true
    },
    author: {
      type: [Schema.Types.ObjectId],
      ref: "User",
      required: true,
    },
    blog_id: {
      type: String,
      required: true,
      unique: true,
    },
    des: {
      type: String,
      // required:true
    },
    activity: {
      total_like: {
        type: Number,
        default: 0,
      },
      total_comment: {
        type: Number,
        default: 0,
      },
      total_parent_comment: {
        type: Number,
        default: 0,
      },
      total_read: {
        type: Number,
        default: 0,
      },
    },
    comment: {
      type: [Schema.Types.ObjectId],
      ref: "Comment",
    },
    draft: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: {
      createdAt: "published_at",
      updatedAt: "updated_at",
    },
  }
);

const Blog = mongoose.model("Blog", BlogSchema);
export default Blog;
