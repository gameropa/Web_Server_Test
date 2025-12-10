use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};
use chrono::{DateTime, Utc};

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id: i32,
    pub username: String,
    pub email: String,
    pub display_name: String,
    pub bio: String,
    pub created_at: String,
    pub updated_at: String,
    pub post_count: i32,
    pub follower_count: i32,
    pub following_count: i32,
}

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct Post {
    pub id: i32,
    pub user_id: i32,
    pub content: String,
    pub created_at: String,
    pub updated_at: String,
    pub like_count: i32,
    pub comment_count: i32,
    pub views: i32,
}

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct Comment {
    pub id: i32,
    pub post_id: i32,
    pub user_id: i32,
    pub text: String,
    pub created_at: String,
    pub like_count: i32,
}

pub struct Database {
    users: Arc<Mutex<HashMap<i32, User>>>,
    posts: Arc<Mutex<HashMap<i32, Post>>>,
    comments: Arc<Mutex<HashMap<i32, Comment>>>,
    likes: Arc<Mutex<HashSet<(i32, i32)>>>,
    followers: Arc<Mutex<HashMap<i32, HashSet<i32>>>>,
    user_id: Arc<Mutex<i32>>,
    post_id: Arc<Mutex<i32>>,
    comment_id: Arc<Mutex<i32>>,
}

impl Clone for Database {
    fn clone(&self) -> Self {
        Database {
            users: Arc::clone(&self.users),
            posts: Arc::clone(&self.posts),
            comments: Arc::clone(&self.comments),
            likes: Arc::clone(&self.likes),
            followers: Arc::clone(&self.followers),
            user_id: Arc::clone(&self.user_id),
            post_id: Arc::clone(&self.post_id),
            comment_id: Arc::clone(&self.comment_id),
        }
    }
}

impl Database {
    pub fn new() -> Self {
        Database {
            users: Arc::new(Mutex::new(HashMap::new())),
            posts: Arc::new(Mutex::new(HashMap::new())),
            comments: Arc::new(Mutex::new(HashMap::new())),
            likes: Arc::new(Mutex::new(HashSet::new())),
            followers: Arc::new(Mutex::new(HashMap::new())),
            user_id: Arc::new(Mutex::new(0)),
            post_id: Arc::new(Mutex::new(0)),
            comment_id: Arc::new(Mutex::new(0)),
        }
    }

    pub fn create_user(&self, username: String, email: String, display_name: String) -> User {
        let mut id = self.user_id.lock().unwrap();
        *id += 1;
        let user_id = *id;

        let user = User {
            id: user_id,
            username,
            email,
            display_name,
            bio: String::new(),
            created_at: Utc::now().to_rfc3339(),
            updated_at: Utc::now().to_rfc3339(),
            post_count: 0,
            follower_count: 0,
            following_count: 0,
        };

        self.users.lock().unwrap().insert(user_id, user.clone());
        self.followers.lock().unwrap().insert(user_id, HashSet::new());
        user
    }

    pub fn get_user(&self, id: i32) -> Option<User> {
        self.users.lock().unwrap().get(&id).cloned()
    }

    pub fn get_all_users(&self) -> Vec<User> {
        self.users.lock().unwrap().values().cloned().collect()
    }

    pub fn create_post(&self, user_id: i32, content: String) -> Post {
        let mut id = self.post_id.lock().unwrap();
        *id += 1;
        let post_id = *id;

        let post = Post {
            id: post_id,
            user_id,
            content,
            created_at: Utc::now().to_rfc3339(),
            updated_at: Utc::now().to_rfc3339(),
            like_count: 0,
            comment_count: 0,
            views: 0,
        };

        self.posts.lock().unwrap().insert(post_id, post.clone());
        if let Some(mut user) = self.users.lock().unwrap().get_mut(&user_id) {
            user.post_count += 1;
        }
        post
    }

    pub fn get_post(&self, id: i32) -> Option<Post> {
        let mut posts = self.posts.lock().unwrap();
        if let Some(post) = posts.get_mut(&id) {
            post.views += 1;
            return Some(post.clone());
        }
        None
    }

    pub fn get_posts_by_user(&self, user_id: i32) -> Vec<Post> {
        self.posts
            .lock()
            .unwrap()
            .values()
            .filter(|p| p.user_id == user_id)
            .cloned()
            .collect()
    }

    pub fn get_feed(&self, user_id: i32, limit: usize) -> Vec<Post> {
        let followers = self.followers.lock().unwrap();
        let following = followers.get(&user_id).cloned().unwrap_or_default();

        let mut feed: Vec<Post> = self
            .posts
            .lock()
            .unwrap()
            .values()
            .filter(|p| following.contains(&p.user_id) || p.user_id == user_id)
            .cloned()
            .collect();

        feed.sort_by(|a, b| b.created_at.cmp(&a.created_at));
        feed.truncate(limit);
        feed
    }

    pub fn add_comment(&self, post_id: i32, user_id: i32, text: String) -> Comment {
        let mut id = self.comment_id.lock().unwrap();
        *id += 1;
        let comment_id = *id;

        let comment = Comment {
            id: comment_id,
            post_id,
            user_id,
            text,
            created_at: Utc::now().to_rfc3339(),
            like_count: 0,
        };

        self.comments.lock().unwrap().insert(comment_id, comment.clone());
        if let Some(mut post) = self.posts.lock().unwrap().get_mut(&post_id) {
            post.comment_count += 1;
        }
        comment
    }

    pub fn get_comments(&self, post_id: i32) -> Vec<Comment> {
        self.comments
            .lock()
            .unwrap()
            .values()
            .filter(|c| c.post_id == post_id)
            .cloned()
            .collect()
    }

    pub fn like_post(&self, post_id: i32, user_id: i32) -> bool {
        let key = (post_id, user_id);
        let mut likes = self.likes.lock().unwrap();
        if likes.contains(&key) {
            return false;
        }
        likes.insert(key);
        if let Some(mut post) = self.posts.lock().unwrap().get_mut(&post_id) {
            post.like_count += 1;
        }
        true
    }

    pub fn unlike_post(&self, post_id: i32, user_id: i32) -> bool {
        let key = (post_id, user_id);
        let mut likes = self.likes.lock().unwrap();
        if !likes.contains(&key) {
            return false;
        }
        likes.remove(&key);
        if let Some(mut post) = self.posts.lock().unwrap().get_mut(&post_id) {
            if post.like_count > 0 {
                post.like_count -= 1;
            }
        }
        true
    }

    pub fn follow(&self, follower_id: i32, following_id: i32) -> bool {
        if follower_id == following_id {
            return false;
        }

        let mut followers = self.followers.lock().unwrap();
        let following_set = followers.entry(following_id).or_insert_with(HashSet::new);

        if !following_set.contains(&follower_id) {
            following_set.insert(follower_id);

            if let Some(mut user) = self.users.lock().unwrap().get_mut(&following_id) {
                user.follower_count += 1;
            }
            if let Some(mut user) = self.users.lock().unwrap().get_mut(&follower_id) {
                user.following_count += 1;
            }
            return true;
        }
        false
    }

    pub fn unfollow(&self, follower_id: i32, following_id: i32) -> bool {
        let mut followers = self.followers.lock().unwrap();
        if let Some(following_set) = followers.get_mut(&following_id) {
            if following_set.contains(&follower_id) {
                following_set.remove(&follower_id);

                if let Some(mut user) = self.users.lock().unwrap().get_mut(&following_id) {
                    if user.follower_count > 0 {
                        user.follower_count -= 1;
                    }
                }
                if let Some(mut user) = self.users.lock().unwrap().get_mut(&follower_id) {
                    if user.following_count > 0 {
                        user.following_count -= 1;
                    }
                }
                return true;
            }
        }
        false
    }

    pub fn get_followers(&self, user_id: i32) -> Vec<User> {
        let followers = self.followers.lock().unwrap();
        let follower_ids = followers.get(&user_id).cloned().unwrap_or_default();

        let users = self.users.lock().unwrap();
        follower_ids
            .iter()
            .filter_map(|id| users.get(id).cloned())
            .collect()
    }
}
