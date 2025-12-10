using System;
using System.Net.Http;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Diagnostics;

class LoadTest
{
    private static readonly string BASE_URL = "http://localhost:3002";
    private static readonly HttpClient client = new();

    static async Task Main()
    {
        Console.WriteLine("\n========================================");
        Console.WriteLine("  C#/.NET - LOAD TEST");
        Console.WriteLine("========================================\n");

        var startTime = Stopwatch.GetTimestamp();

        // Create users
        Console.WriteLine("Creating 100 users...");
        var userIds = new List<int>();
        for (int i = 0; i < 100; i++)
        {
            var res = await MakeRequest("POST", "/api/users", new
            {
                username = $"user{i}",
                email = $"user{i}@example.com",
                displayName = $"User {i}",
            });
            if (res != null && res.ContainsKey("id"))
                userIds.Add((int)(long)res["id"]);
        }

        // Create posts
        Console.WriteLine("Creating 500 posts...");
        var postIds = new List<int>();
        for (int i = 0; i < 500; i++)
        {
            var res = await MakeRequest("POST", "/api/posts", new
            {
                userId = userIds[i % userIds.Count],
                content = $"Post #{i} - Lorem ipsum dolor sit amet",
            });
            if (res != null && res.ContainsKey("id"))
                postIds.Add((int)(long)res["id"]);
        }

        // Add comments
        Console.WriteLine("Adding 1000 comments...");
        for (int i = 0; i < 1000; i++)
        {
            await MakeRequest("POST", "/api/comments", new
            {
                postId = postIds[i % postIds.Count],
                userId = userIds[i % userIds.Count],
                text = $"Comment #{i} - Great post!",
            });
        }

        // Like posts
        Console.WriteLine("Liking 2000 times...");
        int likeCount = 0;
        for (int i = 0; i < 2000; i++)
        {
            var res = await MakeRequest("POST", "/api/likes", new
            {
                postId = postIds[i % postIds.Count],
                userId = userIds[(i + 1) % userIds.Count],
            });
            if (res != null && res.ContainsKey("success"))
                likeCount++;
        }

        // Follow users
        Console.WriteLine("Creating 500 follow relationships...");
        int followCount = 0;
        for (int i = 0; i < 500; i++)
        {
            var res = await MakeRequest("POST", "/api/follow", new
            {
                followerId = userIds[i % userIds.Count],
                followingId = userIds[(i + 1) % userIds.Count],
            });
            if (res != null && res.ContainsKey("success"))
                followCount++;
        }

        // Fetch feeds
        Console.WriteLine("Fetching 100 feeds...");
        for (int i = 0; i < 100; i++)
        {
            await client.GetAsync($"{BASE_URL}/api/users/{userIds[i]}/feed");
        }

        // Fetch posts with comments
        Console.WriteLine("Fetching posts with comments...");
        for (int i = 0; i < 100; i++)
        {
            await client.GetAsync($"{BASE_URL}/api/posts/{postIds[i]}");
            await client.GetAsync($"{BASE_URL}/api/posts/{postIds[i]}/comments");
        }

        var totalTime = Stopwatch.GetElapsedTime(startTime).TotalMilliseconds;

        Console.WriteLine("\n========================================");
        Console.WriteLine("           LOAD TEST RESULTS");
        Console.WriteLine("========================================");
        Console.WriteLine($"Users Created:        100");
        Console.WriteLine($"Posts Created:        500");
        Console.WriteLine($"Comments Added:       1000");
        Console.WriteLine($"Likes Successful:     {likeCount}");
        Console.WriteLine($"Follows Successful:   {followCount}");
        Console.WriteLine($"Total Execution Time: {totalTime:F0} ms");
        Console.WriteLine($"Requests/sec:         {(5000 * 1000 / totalTime):F2}");
        Console.WriteLine("========================================\n");
    }

    static async Task<Dictionary<string, object>> MakeRequest(string method, string path, object body)
    {
        try
        {
            var request = new HttpRequestMessage(new HttpMethod(method), $"{BASE_URL}{path}");
            if (body != null)
            {
                var json = System.Text.Json.JsonSerializer.Serialize(body);
                request.Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
            }
            var response = await client.SendAsync(request);
            var content = await response.Content.ReadAsStringAsync();
            return System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, object>>(content);
        }
        catch { return null; }
    }
}
