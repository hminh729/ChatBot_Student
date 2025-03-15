import nodemailer from "nodemailer";
import dotenv from "dotenv"

dotenv.config();

export const sendEmail = async ({email,subject,html }) => {
   const transporter = nodemailer.createTransport({
      service: "Gmail",
      auth: {
        user: process.env.myEmail,
        pass: process.env.myEmailPassword
      },
    }); 
    const message = {
      from: 'Happy Travel',
      to: email, 
      subject: subject, 
      html: html, 
    }
    const info = await transporter.sendMail(message);
    return info;
};
