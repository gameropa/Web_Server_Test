import { db } from "./database.js";

// User Handlers
export const userHandlers = {
  createUser: (req, res) => {
    const { username, email, displayName } = req.body;
    if (!username || !email || !displayName) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const user = db.createUser(username, email, displayName);
    res.status(201).json(user);
  },

  getUser: (req, res) => {
    const user = db.getUser(req.params.id);
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  },

  updateUser: (req, res) => {
    const user = db.updateUser(req.params.id, req.body);
    if (!user) return res.status(404).json({ error: "User not found" });
    res.json(user);
  },

  getAllUsers: (req, res) => {
    const users = db.getAllUsers();
    res.json(users);
  },
};

// Post Handlers
export const postHandlers = {
  createPost: (req, res) => {
    const { userId, content } = req.body;
    if (!userId || !content) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const post = db.createPost(userId, content);
    res.status(201).json(post);
  },

  getPost: (req, res) => {
    const post = db.getPost(req.params.id);
    if (!post) return res.status(404).json({ error: "Post not found" });
    res.json(post);
  },

  getUserPosts: (req, res) => {
    const posts = db.getPostsByUser(req.params.userId);
    res.json(posts);
  },

  getFeed: (req, res) => {
    const limit = parseInt(req.query.limit) || 20;
    const feed = db.getFeed(req.params.userId, limit);
    res.json(feed);
  },
};

// Comment Handlers
export const commentHandlers = {
  addComment: (req, res) => {
    const { postId, userId, text } = req.body;
    if (!postId || !userId || !text) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const comment = db.addComment(postId, userId, text);
    res.status(201).json(comment);
  },

  getComments: (req, res) => {
    const comments = db.getComments(req.params.postId);
    res.json(comments);
  },
};

// Like Handlers
export const likeHandlers = {
  likePost: (req, res) => {
    const { postId, userId } = req.body;
    if (!postId || !userId) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const success = db.likePost(postId, userId);
    if (!success) return res.status(400).json({ error: "Already liked" });
    res.status(201).json({ success: true });
  },

  unlikePost: (req, res) => {
    const { postId, userId } = req.body;
    const success = db.unlikePost(postId, userId);
    if (!success) return res.status(400).json({ error: "Not liked" });
    res.json({ success: true });
  },

  isPostLiked: (req, res) => {
    const liked = db.isPostLiked(req.params.postId, req.params.userId);
    res.json({ liked });
  },
};

// Follow Handlers
export const followHandlers = {
  follow: (req, res) => {
    const { followerId, followingId } = req.body;
    if (!followerId || !followingId) {
      return res.status(400).json({ error: "Missing required fields" });
    }
    const success = db.follow(followerId, followingId);
    if (!success) return res.status(400).json({ error: "Already following" });
    res.status(201).json({ success: true });
  },

  unfollow: (req, res) => {
    const { followerId, followingId } = req.body;
    const success = db.unfollow(followerId, followingId);
    if (!success) return res.status(400).json({ error: "Not following" });
    res.json({ success: true });
  },

  getFollowers: (req, res) => {
    const followers = db.getFollowers(req.params.userId);
    res.json(followers);
  },
};
