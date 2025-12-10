// In-Memory Database Simulation
export class Database {
  constructor() {
    this.users = new Map();
    this.posts = new Map();
    this.comments = new Map();
    this.likes = new Map();
    this.followers = new Map();
    this.notifications = new Map();
    this.userId = 0;
    this.postId = 0;
    this.commentId = 0;
    this.likeId = 0;
  }

  // User Operations
  createUser(username, email, displayName) {
    const id = ++this.userId;
    const user = {
      id,
      username,
      email,
      displayName,
      bio: "",
      createdAt: new Date(),
      updatedAt: new Date(),
      postCount: 0,
      followerCount: 0,
      followingCount: 0,
    };
    this.users.set(id, user);
    this.followers.set(id, new Set());
    return user;
  }

  getUser(id) {
    return this.users.get(parseInt(id));
  }

  updateUser(id, updates) {
    const user = this.users.get(parseInt(id));
    if (!user) return null;
    Object.assign(user, updates, { updatedAt: new Date() });
    return user;
  }

  getAllUsers() {
    return Array.from(this.users.values());
  }

  // Post Operations
  createPost(userId, content) {
    const id = ++this.postId;
    const post = {
      id,
      userId: parseInt(userId),
      content,
      createdAt: new Date(),
      updatedAt: new Date(),
      likeCount: 0,
      commentCount: 0,
      views: 0,
    };
    this.posts.set(id, post);
    const user = this.users.get(parseInt(userId));
    if (user) user.postCount++;
    return post;
  }

  getPost(id) {
    const post = this.posts.get(parseInt(id));
    if (post) post.views++;
    return post;
  }

  getPostsByUser(userId) {
    return Array.from(this.posts.values()).filter(
      (p) => p.userId === parseInt(userId)
    );
  }

  getFeed(userId, limit = 20) {
    const following = this.followers.get(parseInt(userId)) || new Set();
    return Array.from(this.posts.values())
      .filter((p) => following.has(p.userId) || p.userId === parseInt(userId))
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, limit);
  }

  // Comment Operations
  addComment(postId, userId, text) {
    const id = ++this.commentId;
    const comment = {
      id,
      postId: parseInt(postId),
      userId: parseInt(userId),
      text,
      createdAt: new Date(),
      likeCount: 0,
    };
    this.comments.set(id, comment);
    const post = this.posts.get(parseInt(postId));
    if (post) post.commentCount++;
    return comment;
  }

  getComments(postId) {
    return Array.from(this.comments.values()).filter(
      (c) => c.postId === parseInt(postId)
    );
  }

  // Like Operations
  likePost(postId, userId) {
    const key = `${postId}-${userId}`;
    if (this.likes.has(key)) return false; // Already liked
    const id = ++this.likeId;
    this.likes.set(key, { id, postId: parseInt(postId), userId: parseInt(userId) });
    const post = this.posts.get(parseInt(postId));
    if (post) post.likeCount++;
    return true;
  }

  unlikePost(postId, userId) {
    const key = `${postId}-${userId}`;
    if (!this.likes.has(key)) return false;
    this.likes.delete(key);
    const post = this.posts.get(parseInt(postId));
    if (post && post.likeCount > 0) post.likeCount--;
    return true;
  }

  isPostLiked(postId, userId) {
    return this.likes.has(`${postId}-${userId}`);
  }

  // Follow Operations
  follow(followerId, followingId) {
    if (followerId === followingId) return false;
    const followers = this.followers.get(followingId);
    if (!followers.has(followerId)) {
      followers.add(followerId);
      const following = this.followers.get(followerId) || new Set();
      this.followers.set(followerId, following);
      const user = this.users.get(followingId);
      if (user) user.followerCount++;
      const follower = this.users.get(followerId);
      if (follower) follower.followingCount++;
      return true;
    }
    return false;
  }

  unfollow(followerId, followingId) {
    const followers = this.followers.get(followingId);
    if (followers.has(followerId)) {
      followers.delete(followerId);
      const user = this.users.get(followingId);
      if (user && user.followerCount > 0) user.followerCount--;
      const follower = this.users.get(followerId);
      if (follower && follower.followingCount > 0) follower.followingCount--;
      return true;
    }
    return false;
  }

  getFollowers(userId) {
    const followers = this.followers.get(parseInt(userId)) || new Set();
    return Array.from(followers).map((id) => this.users.get(id));
  }
}

export const db = new Database();
