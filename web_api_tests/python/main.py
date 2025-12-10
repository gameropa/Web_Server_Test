from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from collections import defaultdict
import uvicorn

# Models
class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    displayName: str
    bio: str = ""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    postCount: int = 0
    followerCount: int = 0
    followingCount: int = 0

class Post(BaseModel):
    id: Optional[int] = None
    userId: int
    content: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    likeCount: int = 0
    commentCount: int = 0
    views: int = 0

class Comment(BaseModel):
    id: Optional[int] = None
    postId: int
    userId: int
    text: str
    createdAt: Optional[datetime] = None
    likeCount: int = 0

class Like(BaseModel):
    postId: int
    userId: int

class Follow(BaseModel):
    followerId: int
    followingId: int

# In-Memory Database
class Database:
    def __init__(self):
        self.users = {}
        self.posts = {}
        self.comments = {}
        self.likes = set()
        self.followers = defaultdict(set)
        self.user_id = 0
        self.post_id = 0
        self.comment_id = 0

    def create_user(self, username: str, email: str, display_name: str) -> User:
        self.user_id += 1
        user = User(
            id=self.user_id,
            username=username,
            email=email,
            displayName=display_name,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        self.users[self.user_id] = user
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def update_user(self, user_id: int, updates: dict) -> Optional[User]:
        user = self.users.get(user_id)
        if user:
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updatedAt = datetime.now()
        return user

    def get_all_users(self) -> List[User]:
        return list(self.users.values())

    def create_post(self, user_id: int, content: str) -> Post:
        self.post_id += 1
        post = Post(
            id=self.post_id,
            userId=user_id,
            content=content,
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        self.posts[self.post_id] = post
        user = self.users.get(user_id)
        if user:
            user.postCount += 1
        return post

    def get_post(self, post_id: int) -> Optional[Post]:
        post = self.posts.get(post_id)
        if post:
            post.views += 1
        return post

    def get_posts_by_user(self, user_id: int) -> List[Post]:
        return [p for p in self.posts.values() if p.userId == user_id]

    def get_feed(self, user_id: int, limit: int = 20) -> List[Post]:
        following = self.followers.get(user_id, set())
        feed = [p for p in self.posts.values() 
                if p.userId in following or p.userId == user_id]
        feed.sort(key=lambda x: x.createdAt, reverse=True)
        return feed[:limit]

    def add_comment(self, post_id: int, user_id: int, text: str) -> Comment:
        self.comment_id += 1
        comment = Comment(
            id=self.comment_id,
            postId=post_id,
            userId=user_id,
            text=text,
            createdAt=datetime.now(),
        )
        self.comments[self.comment_id] = comment
        post = self.posts.get(post_id)
        if post:
            post.commentCount += 1
        return comment

    def get_comments(self, post_id: int) -> List[Comment]:
        return [c for c in self.comments.values() if c.postId == post_id]

    def like_post(self, post_id: int, user_id: int) -> bool:
        key = (post_id, user_id)
        if key in self.likes:
            return False
        self.likes.add(key)
        post = self.posts.get(post_id)
        if post:
            post.likeCount += 1
        return True

    def unlike_post(self, post_id: int, user_id: int) -> bool:
        key = (post_id, user_id)
        if key not in self.likes:
            return False
        self.likes.remove(key)
        post = self.posts.get(post_id)
        if post and post.likeCount > 0:
            post.likeCount -= 1
        return True

    def is_post_liked(self, post_id: int, user_id: int) -> bool:
        return (post_id, user_id) in self.likes

    def follow(self, follower_id: int, following_id: int) -> bool:
        if follower_id == following_id:
            return False
        if follower_id not in self.followers[following_id]:
            self.followers[following_id].add(follower_id)
            user = self.users.get(following_id)
            if user:
                user.followerCount += 1
            follower = self.users.get(follower_id)
            if follower:
                follower.followingCount += 1
            return True
        return False

    def unfollow(self, follower_id: int, following_id: int) -> bool:
        if follower_id in self.followers[following_id]:
            self.followers[following_id].remove(follower_id)
            user = self.users.get(following_id)
            if user and user.followerCount > 0:
                user.followerCount -= 1
            follower = self.users.get(follower_id)
            if follower and follower.followingCount > 0:
                follower.followingCount -= 1
            return True
        return False

    def get_followers(self, user_id: int) -> List[User]:
        follower_ids = self.followers.get(user_id, set())
        return [self.users[uid] for uid in follower_ids if uid in self.users]

# Initialize
app = FastAPI(title="Social Media API - FastAPI")
db = Database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now()}

# User Routes
@app.post("/api/users", response_model=User, status_code=201)
async def create_user(user: User):
    return db.create_user(user.username, user.email, user.displayName)

@app.get("/api/users", response_model=List[User])
async def get_all_users():
    return db.get_all_users()

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, updates: dict):
    user = db.update_user(user_id, updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Post Routes
@app.post("/api/posts", response_model=Post, status_code=201)
async def create_post(post: Post):
    return db.create_post(post.userId, post.content)

@app.get("/api/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    post = db.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/api/users/{user_id}/posts", response_model=List[Post])
async def get_user_posts(user_id: int):
    return db.get_posts_by_user(user_id)

@app.get("/api/users/{user_id}/feed", response_model=List[Post])
async def get_feed(user_id: int, limit: int = 20):
    return db.get_feed(user_id, limit)

# Comment Routes
@app.post("/api/comments", response_model=Comment, status_code=201)
async def add_comment(comment: Comment):
    return db.add_comment(comment.postId, comment.userId, comment.text)

@app.get("/api/posts/{post_id}/comments", response_model=List[Comment])
async def get_comments(post_id: int):
    return db.get_comments(post_id)

# Like Routes
@app.post("/api/likes", status_code=201)
async def like_post(like: Like):
    if db.like_post(like.postId, like.userId):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Already liked")

@app.delete("/api/likes")
async def unlike_post(like: Like):
    if db.unlike_post(like.postId, like.userId):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Not liked")

@app.get("/api/posts/{post_id}/likes/user/{user_id}")
async def is_post_liked(post_id: int, user_id: int):
    return {"liked": db.is_post_liked(post_id, user_id)}

# Follow Routes
@app.post("/api/follow", status_code=201)
async def follow(follow: Follow):
    if db.follow(follow.followerId, follow.followingId):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Already following")

@app.delete("/api/follow")
async def unfollow(follow: Follow):
    if db.unfollow(follow.followerId, follow.followingId):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Not following")

@app.get("/api/users/{user_id}/followers", response_model=List[User])
async def get_followers(user_id: int):
    return db.get_followers(user_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001, log_level="error")
