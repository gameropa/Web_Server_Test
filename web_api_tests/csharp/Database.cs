using System;
using System.Collections.Generic;
using System.Linq;

public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = "";
    public string Email { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public string Bio { get; set; } = "";
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public int PostCount { get; set; } = 0;
    public int FollowerCount { get; set; } = 0;
    public int FollowingCount { get; set; } = 0;
}

public class Post
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public string Content { get; set; } = "";
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public int LikeCount { get; set; } = 0;
    public int CommentCount { get; set; } = 0;
    public int Views { get; set; } = 0;
}

public class Comment
{
    public int Id { get; set; }
    public int PostId { get; set; }
    public int UserId { get; set; }
    public string Text { get; set; } = "";
    public DateTime CreatedAt { get; set; }
    public int LikeCount { get; set; } = 0;
}

public class Database
{
    private Dictionary<int, User> users = new();
    private Dictionary<int, Post> posts = new();
    private Dictionary<int, Comment> comments = new();
    private HashSet<(int, int)> likes = new();
    private Dictionary<int, HashSet<int>> followers = new();
    private int userId = 0;
    private int postId = 0;
    private int commentId = 0;

    public User CreateUser(string username, string email, string displayName)
    {
        int id = ++userId;
        var user = new User
        {
            Id = id,
            Username = username,
            Email = email,
            DisplayName = displayName,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now,
        };
        users[id] = user;
        followers[id] = new HashSet<int>();
        return user;
    }

    public User GetUser(int id) => users.ContainsKey(id) ? users[id] : null;

    public User UpdateUser(int id, Dictionary<string, object> updates)
    {
        if (!users.ContainsKey(id)) return null;
        var user = users[id];
        foreach (var kvp in updates)
        {
            switch (kvp.Key)
            {
                case "bio": user.Bio = (string)kvp.Value; break;
                case "displayName": user.DisplayName = (string)kvp.Value; break;
            }
        }
        user.UpdatedAt = DateTime.Now;
        return user;
    }

    public List<User> GetAllUsers() => users.Values.ToList();

    public Post CreatePost(int userId, string content)
    {
        int id = ++postId;
        var post = new Post
        {
            Id = id,
            UserId = userId,
            Content = content,
            CreatedAt = DateTime.Now,
            UpdatedAt = DateTime.Now,
        };
        posts[id] = post;
        if (users.ContainsKey(userId)) users[userId].PostCount++;
        return post;
    }

    public Post GetPost(int id)
    {
        if (posts.ContainsKey(id))
        {
            posts[id].Views++;
            return posts[id];
        }
        return null;
    }

    public List<Post> GetPostsByUser(int userId) =>
        posts.Values.Where(p => p.UserId == userId).ToList();

    public List<Post> GetFeed(int userId, int limit = 20)
    {
        var following = followers.ContainsKey(userId) ? followers[userId] : new HashSet<int>();
        return posts.Values
            .Where(p => following.Contains(p.UserId) || p.UserId == userId)
            .OrderByDescending(p => p.CreatedAt)
            .Take(limit)
            .ToList();
    }

    public Comment AddComment(int postId, int userId, string text)
    {
        int id = ++commentId;
        var comment = new Comment
        {
            Id = id,
            PostId = postId,
            UserId = userId,
            Text = text,
            CreatedAt = DateTime.Now,
        };
        comments[id] = comment;
        if (posts.ContainsKey(postId)) posts[postId].CommentCount++;
        return comment;
    }

    public List<Comment> GetComments(int postId) =>
        comments.Values.Where(c => c.PostId == postId).ToList();

    public bool LikePost(int postId, int userId)
    {
        var key = (postId, userId);
        if (likes.Contains(key)) return false;
        likes.Add(key);
        if (posts.ContainsKey(postId)) posts[postId].LikeCount++;
        return true;
    }

    public bool UnlikePost(int postId, int userId)
    {
        var key = (postId, userId);
        if (!likes.Contains(key)) return false;
        likes.Remove(key);
        if (posts.ContainsKey(postId) && posts[postId].LikeCount > 0)
            posts[postId].LikeCount--;
        return true;
    }

    public bool IsPostLiked(int postId, int userId) =>
        likes.Contains((postId, userId));

    public bool Follow(int followerId, int followingId)
    {
        if (followerId == followingId) return false;
        if (!followers.ContainsKey(followingId))
            followers[followingId] = new HashSet<int>();
        if (!followers[followingId].Contains(followerId))
        {
            followers[followingId].Add(followerId);
            if (users.ContainsKey(followingId)) users[followingId].FollowerCount++;
            if (users.ContainsKey(followerId)) users[followerId].FollowingCount++;
            return true;
        }
        return false;
    }

    public bool Unfollow(int followerId, int followingId)
    {
        if (!followers.ContainsKey(followingId)) return false;
        if (followers[followingId].Contains(followerId))
        {
            followers[followingId].Remove(followerId);
            if (users.ContainsKey(followingId) && users[followingId].FollowerCount > 0)
                users[followingId].FollowerCount--;
            if (users.ContainsKey(followerId) && users[followerId].FollowingCount > 0)
                users[followerId].FollowingCount--;
            return true;
        }
        return false;
    }

    public List<User> GetFollowers(int userId)
    {
        if (!followers.ContainsKey(userId)) return new List<User>();
        return followers[userId]
            .Where(id => users.ContainsKey(id))
            .Select(id => users[id])
            .ToList();
    }
}
