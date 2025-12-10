using System;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);

// Register Database singleton
var db = new Database();
builder.Services.AddSingleton(db);
builder.Services.AddCors();

var app = builder.Build();

app.UseCors(x => x
    .AllowAnyMethod()
    .AllowAnyHeader()
    .SetIsOriginAllowed(origin => true));

// Health Check
app.MapGet("/health", () => new { status = "ok", timestamp = DateTime.Now });

// User Routes
app.MapPost("/api/users", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var username = root.TryGetProperty("username", out var u) ? u.GetString() ?? string.Empty : string.Empty;
    var email = root.TryGetProperty("email", out var e) ? e.GetString() ?? string.Empty : string.Empty;
    var displayName = root.TryGetProperty("displayName", out var d) ? d.GetString() ?? string.Empty : string.Empty;

    var user = db.CreateUser(username, email, displayName);
    ctx.Response.StatusCode = 201;
    await ctx.Response.WriteAsJsonAsync(user);
});

app.MapGet("/api/users", (Database db) => db.GetAllUsers());

app.MapGet("/api/users/{id}", async (int id, Database db, HttpContext ctx) =>
{
    var user = db.GetUser(id);
    if (user == null)
    {
        ctx.Response.StatusCode = 404;
        return;
    }
    await ctx.Response.WriteAsJsonAsync(user);
});

app.MapPut("/api/users/{id}", async (int id, HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var updates = new Dictionary<string, object>();

    if (doc.RootElement.TryGetProperty("username", out var u) && u.ValueKind == JsonValueKind.String)
        updates["username"] = u.GetString() ?? string.Empty;
    if (doc.RootElement.TryGetProperty("email", out var e) && e.ValueKind == JsonValueKind.String)
        updates["email"] = e.GetString() ?? string.Empty;
    if (doc.RootElement.TryGetProperty("displayName", out var d) && d.ValueKind == JsonValueKind.String)
        updates["displayName"] = d.GetString() ?? string.Empty;
    if (doc.RootElement.TryGetProperty("bio", out var b) && b.ValueKind == JsonValueKind.String)
        updates["bio"] = b.GetString() ?? string.Empty;

    var user = db.UpdateUser(id, updates);
    if (user == null)
    {
        ctx.Response.StatusCode = 404;
        return;
    }
    await ctx.Response.WriteAsJsonAsync(user);
});

// Post Routes
app.MapPost("/api/posts", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var userId = root.TryGetProperty("userId", out var u) && u.TryGetInt32(out var uid) ? uid : 0;
    var content = root.TryGetProperty("content", out var c) ? c.GetString() ?? string.Empty : string.Empty;

    var post = db.CreatePost(userId, content);
    ctx.Response.StatusCode = 201;
    await ctx.Response.WriteAsJsonAsync(post);
});

app.MapGet("/api/posts/{id}", async (int id, Database db, HttpContext ctx) =>
{
    var post = db.GetPost(id);
    if (post == null)
    {
        ctx.Response.StatusCode = 404;
        return;
    }
    await ctx.Response.WriteAsJsonAsync(post);
});

app.MapGet("/api/users/{userId}/posts", (int userId, Database db) =>
    db.GetPostsByUser(userId));

app.MapGet("/api/users/{userId}/feed", (int userId, Database db) =>
    db.GetFeed(userId, 20));

// Comment Routes
app.MapPost("/api/comments", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var postId = root.TryGetProperty("postId", out var p) && p.TryGetInt32(out var pid) ? pid : 0;
    var userId = root.TryGetProperty("userId", out var u) && u.TryGetInt32(out var uid) ? uid : 0;
    var text = root.TryGetProperty("text", out var t) ? t.GetString() ?? string.Empty : string.Empty;

    var comment = db.AddComment(postId, userId, text);
    ctx.Response.StatusCode = 201;
    await ctx.Response.WriteAsJsonAsync(comment);
});

app.MapGet("/api/posts/{postId}/comments", (int postId, Database db) =>
    db.GetComments(postId));

// Like Routes
app.MapPost("/api/likes", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var postId = root.TryGetProperty("postId", out var p) && p.TryGetInt32(out var pid) ? pid : 0;
    var userId = root.TryGetProperty("userId", out var u) && u.TryGetInt32(out var uid) ? uid : 0;

    if (db.LikePost(postId, userId))
    {
        ctx.Response.StatusCode = 201;
        await ctx.Response.WriteAsJsonAsync(new { success = true });
    }
    else
    {
        ctx.Response.StatusCode = 400;
        await ctx.Response.WriteAsJsonAsync(new { error = "Already liked" });
    }
});

app.MapDelete("/api/likes", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var postId = root.TryGetProperty("postId", out var p) && p.TryGetInt32(out var pid) ? pid : 0;
    var userId = root.TryGetProperty("userId", out var u) && u.TryGetInt32(out var uid) ? uid : 0;

    if (db.UnlikePost(postId, userId))
    {
        await ctx.Response.WriteAsJsonAsync(new { success = true });
    }
    else
    {
        ctx.Response.StatusCode = 400;
        await ctx.Response.WriteAsJsonAsync(new { error = "Not liked" });
    }
});

app.MapGet("/api/posts/{postId}/likes/user/{userId}", (int postId, int userId, Database db) =>
    new { liked = db.IsPostLiked(postId, userId) });

// Follow Routes
app.MapPost("/api/follow", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var followerId = root.TryGetProperty("followerId", out var f) && f.TryGetInt32(out var fid) ? fid : 0;
    var followingId = root.TryGetProperty("followingId", out var t) && t.TryGetInt32(out var tid) ? tid : 0;

    if (db.Follow(followerId, followingId))
    {
        ctx.Response.StatusCode = 201;
        await ctx.Response.WriteAsJsonAsync(new { success = true });
    }
    else
    {
        ctx.Response.StatusCode = 400;
        await ctx.Response.WriteAsJsonAsync(new { error = "Already following" });
    }
});

app.MapDelete("/api/follow", async (HttpContext ctx, Database db) =>
{
    var doc = await JsonDocument.ParseAsync(ctx.Request.Body);
    var root = doc.RootElement;

    var followerId = root.TryGetProperty("followerId", out var f) && f.TryGetInt32(out var fid) ? fid : 0;
    var followingId = root.TryGetProperty("followingId", out var t) && t.TryGetInt32(out var tid) ? tid : 0;

    if (db.Unfollow(followerId, followingId))
    {
        await ctx.Response.WriteAsJsonAsync(new { success = true });
    }
    else
    {
        ctx.Response.StatusCode = 400;
        await ctx.Response.WriteAsJsonAsync(new { error = "Not following" });
    }
});

app.MapGet("/api/users/{userId}/followers", (int userId, Database db) =>
    db.GetFollowers(userId));

Console.WriteLine("[C#/.NET] Server running on port 3002");
app.Run("http://0.0.0.0:3002");

// Extension method for reading JSON from HttpRequest
static class HttpRequestExtensions
{
    public static async Task<T?> ReadAsJsonAsync<T>(this HttpRequest request)
    {
        return await JsonSerializer.DeserializeAsync<T>(request.Body);
    }
}
