import mongoose from "mongoose";
import Schema from "mongoose";

const UserSchema = new mongoose.Schema(
  {
    information:{
      fullname:{
        type:String,
        required:true,
      },
      username:{
        type:String,
        required:true,
        unique:true,
      },
      email:{
        type:String,
        required:true,
        unique:true,
      },
      password:{
        type:String,
        required:true,
      },
      sex:{
        type:String,
        default:"",
        required :true,
      },
      bios:{
        type:String,
        default:"",
      },
      avatar:{
        type:String,
        default:"",
      }
    },
    social_links:{
      youtube:{
        type:String,
        default:"",
      },
      instagram:{
        type:String,
        default:"",
      },
      facebook:{
        type:String,
        default:"",
      },
      x:{
        type:String,
        default:"",
      },
      tiktok:{
        type:String,
        default:"",
      }
    },
    acc_information:{
      total_blogs:{
        type:Number,
        default:0,
      },
      total_reads:{
        type:Number,
        default:0,
      }
    },
    isGoogleUser:{
      type:Boolean,
      default:false,
    }, 
    blogs:{
      type: [Schema.Types.ObjectId ],
      ref: 'Blog',
      default: [],
    }
  },
  {
    timestamps: true,
  }
);

const User = mongoose.model("User", UserSchema);

export default User;
