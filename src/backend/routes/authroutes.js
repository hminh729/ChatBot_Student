import express from "express";
import {
  PostSignup,
  PostLogin,
  PostLogout,
  resetPassword,
  forgotPassword,
} from "../controllers/auth.controller.js";
// import authProtect from "../middleware/auth.middelware.js";

const route = express.Router();
route.post("/signup", PostSignup);
route.post("/login", PostLogin);
route.post("/logout", PostLogout);
route.post("/forgotPassword", forgotPassword);
route.post("/resetPassword/:token", resetPassword);

export default route;
