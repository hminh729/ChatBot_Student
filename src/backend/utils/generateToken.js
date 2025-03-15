import jwt from "jsonwebtoken";
import dotenv from "dotenv";

dotenv.config();

export const generateAccessToken = (userId) => {
  const acccessToken = jwt.sign({ userId }, process.env.JWT_KEY, {
    expiresIn: "1m",
  });
  return acccessToken;
};

export const generateRefreshToken = (userId) => {
  const refreshToken = jwt.sign({ userId }, process.env.JWT_KEY, {
    expiresIn: "365d",
  });
  return refreshToken;
};

export const generateResetToken = (userId) => {
  const resetToken = jwt.sign({userId }, process.env.JWT_KEY, {
    expiresIn: "5m",
  });
  return resetToken;
};
