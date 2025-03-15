import User from "../models/user.model.js";
import bcryptjs from "bcryptjs";
import {
  generateAccessToken,
  generateRefreshToken,
  generateResetToken,
} from "../utils/generateToken.js";
import {sendEmail} from "../helpers/auth.helper.js"
import jwt from "jsonwebtoken";
import dotenv from "dotenv";

dotenv.config();

export const PostSignup = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ message: "Please fill all the fields" });
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
      return res.status(400).json({ message: "Invalid email format" });
    }

    if (password.length < 6) {
      return res
        .status(400)
        .json({ message: "Password must be at least 6 characters long" });
    }
    const exitsByEmail = await User.findOne({ email: email });
    if (exitsByEmail) {
      return res.status(400).json({ message: "Email already exits" });
    }
    const exitsByUsername = await User.findOne({ username: username });
    if (exitsByUsername) {
      return res.status(400).json({ message: "Username already exits" });
    }
    const salt = bcryptjs.genSaltSync(10);
    const hashPassword = bcryptjs.hashSync(password, salt);
    const newUser = new User({
      username,
      email,
      password: hashPassword,
    });

    const accessToken = generateAccessToken(newUser._id);
    const refreshToken = generateRefreshToken(newUser._id);
    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      sameSite: "strict",
      scure: false,
    });
    await newUser.save();
    console.log("hi");

    res
      .status(201)
      .json({ message: "User createdd", accessToken: accessToken });
  } catch (error) {
    return res.status(500).json({ message: "Server error" });
  }
};

export const PostLogin = async (req, res) => {
  try {
    const { email, password } = req.body;
    const thisUser = await User.findOne({ email: email });
    if (!thisUser) {
      return res.status(404).json({ message: "User not found" });
    }
    const isPasswordmatch = await bcryptjs.compare(password, thisUser.password);
    if (!isPasswordmatch) {
      return res.status(400).json({ message: "Wrong password" });
    }
    const accessToken = generateAccessToken(thisUser._id);
    const refreshToken = generateRefreshToken(thisUser._id);
    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      sameSite: "strict",
      scure: false,
    });
    res
      .status(200)
      .json({ message: "Login successful", accessToken: accessToken });
  } catch (error) {
    return res.status(500).json({ message: "Server error" });
  }
};
export const PostLogout = (req, res) => {
  try {
    res.clearCookie("refreshToken");
    res.status(200).json({ message: "Logout successful" });
  } catch (error) {
    return res.status(500).json({ message: "Server error" });
  }
};

export const resetPassword = async (req, res) => {
    try {
      const resetToken  = req.params.token;
      const { password } = req.body; 
     
      const decoded = jwt.verify(resetToken, process.env.JWT_KEY);
    
      const thisUser = await User.findOne({_id: decoded.userId});
    
    if(!thisUser){
      return res.status(404).json({message:"User not found"})
    }
    const salt = bcryptjs.genSaltSync(10);
    const newHashPassword = bcryptjs.hashSync(password, salt);
    thisUser.password = newHashPassword;
    
    await thisUser.save();
    res.status(200).json({message:"Reset Password Successfully"})
    } catch (error) {
      return res.status(500).json({message:"Error in reset password"})
    }
};

export const forgotPassword = async (req, res) =>{
  try {
    const {email} = req.body;
 
  const thisUser = await User.findOne({email:email});
  if (!thisUser) {
    return res.status(404).json({ message: "Email does not exist" });
  }
  const resetToken = generateResetToken(thisUser._id);
  const resetLink = `http://localhost:3000/api/v1/auth/resetPassword/${resetToken}`
  const subject = "Reset Password";
  const html =`<p>Bạn đã yêu cầu đặt lại mật khẩu. Nhấn vào link bên dưới để đặt lại mật khẩu:</p>
                   <a href="${resetLink}">Đặt lại mật khẩu</a>
                   <p>Link này sẽ hết hạn sau 5 phút.</p>`
  await sendEmail({
    email:email,
    subject: subject,
    html:html
  });
  res.status(200).json({message:"successfully"})
  } catch (error) {
    return res.status(500).json({message:"Server error"})
  }

}
