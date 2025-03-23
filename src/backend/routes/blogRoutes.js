import express from 'express';

import { BlogCreate } from '../controllers/blog.controller.js';

const router = express.Router();

router.post("/create",BlogCreate);



export default router;