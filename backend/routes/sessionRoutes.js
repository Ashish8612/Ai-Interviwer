import express from "express";
import { 
    createSession, 
    deleteSession, 
    endSession, 
    getSessionById, 
    getSessions, 
    submitAnswer
} from "../controllers/sessionController.js";
import { protect } from "../middleware/authMiddleware.js";
import { uploadSingleAudio } from "../middleware/uploadMiddleware.js";

const router = express.Router();

router.use(protect);

router.route("/")
    .get(getSessions)
    .post(createSession);

router.route("/:id")
    .get(getSessionById)
    .delete(deleteSession);

router.route("/:id/submit-answer").post(uploadSingleAudio, submitAnswer);
router.route("/:id/end").post(endSession);

export default router;
