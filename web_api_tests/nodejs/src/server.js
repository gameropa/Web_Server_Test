import express from "express";
import cors from "cors";
import {
  userHandlers,
  postHandlers,
  commentHandlers,
  likeHandlers,
  followHandlers,
} from "./handlers.js";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Health Check
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date() });
});

// User Routes
app.post("/api/users", userHandlers.createUser);
app.get("/api/users", userHandlers.getAllUsers);
app.get("/api/users/:id", userHandlers.getUser);
app.put("/api/users/:id", userHandlers.updateUser);

// Post Routes
app.post("/api/posts", postHandlers.createPost);
app.get("/api/posts/:id", postHandlers.getPost);
app.get("/api/users/:userId/posts", postHandlers.getUserPosts);
app.get("/api/users/:userId/feed", postHandlers.getFeed);

// Comment Routes
app.post("/api/comments", commentHandlers.addComment);
app.get("/api/posts/:postId/comments", commentHandlers.getComments);

// Like Routes
app.post("/api/likes", likeHandlers.likePost);
app.delete("/api/likes", likeHandlers.unlikePost);
app.get("/api/posts/:postId/likes/user/:userId", likeHandlers.isPostLiked);

// Follow Routes
app.post("/api/follow", followHandlers.follow);
app.delete("/api/follow", followHandlers.unfollow);
app.get("/api/users/:userId/followers", followHandlers.getFollowers);

// 404 Handler
app.use((req, res) => {
  res.status(404).json({ error: "Not found" });
});

const server = app.listen(PORT, () => {
  console.log(`[Node.js/Express] Server running on port ${PORT}`);
});

export default server;
