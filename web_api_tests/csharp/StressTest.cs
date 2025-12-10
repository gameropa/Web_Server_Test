using System;
using System.Net.Http;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Diagnostics;

class StressTest
{
    private static readonly string BASE_URL = "http://localhost:3002";
    private static readonly HttpClient client = new();

    static async Task Main()
    {
        Console.WriteLine("\n========================================");
        Console.WriteLine("  C#/.NET - STRESS TEST");
        Console.WriteLine("========================================\n");

        var startTime = Stopwatch.GetTimestamp();

        // Stress 1: Rapid user creation
        Console.WriteLine("Stress Test 1: Rapid User Creation (500 users)...");
        var t1 = Stopwatch.GetTimestamp();
        var userIds = new List<int>();
        for (int i = 0; i < 500; i++)
        {
            var res = await MakeRequest("POST", "/api/users", new
            {
                username = $"stressuser{i}",
                email = $"stressuser{i}@example.com",
                displayName = $"Stress User {i}",
            });
            if (res != null && res.ContainsKey("id"))
                userIds.Add((int)(long)res["id"]);
        }
        var t1Time = Stopwatch.GetElapsedTime(t1).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t1Time:F0}ms ({500000 / t1Time:F0} ops/sec)");

        // Stress 2: Rapid post creation
        Console.WriteLine("Stress Test 2: Rapid Post Creation (2000 posts)...");
        var t2 = Stopwatch.GetTimestamp();
        var postIds = new List<int>();
        for (int i = 0; i < 2000; i++)
        {
            var res = await MakeRequest("POST", "/api/posts", new
            {
                userId = userIds[i % userIds.Count],
                content = $"Stress post {i}",
            });
            if (res != null && res.ContainsKey("id"))
                postIds.Add((int)(long)res["id"]);
        }
        var t2Time = Stopwatch.GetElapsedTime(t2).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t2Time:F0}ms ({2000000 / t2Time:F0} ops/sec)");

        // Stress 3: Massive comment spam
        Console.WriteLine("Stress Test 3: Massive Comment Addition (5000 comments)...");
        var t3 = Stopwatch.GetTimestamp();
        for (int i = 0; i < 5000; i++)
        {
            await MakeRequest("POST", "/api/comments", new
            {
                postId = postIds[i % postIds.Count],
                userId = userIds[i % userIds.Count],
                text = $"Spam comment {i}",
            });
        }
        var t3Time = Stopwatch.GetElapsedTime(t3).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t3Time:F0}ms ({5000000 / t3Time:F0} ops/sec)");

        // Stress 4: Like bombardment
        Console.WriteLine("Stress Test 4: Like Bombardment (5000 likes)...");
        var t4 = Stopwatch.GetTimestamp();
        for (int i = 0; i < 5000; i++)
        {
            await MakeRequest("POST", "/api/likes", new
            {
                postId = postIds[i % postIds.Count],
                userId = userIds[i % userIds.Count],
            });
        }
        var t4Time = Stopwatch.GetElapsedTime(t4).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t4Time:F0}ms ({5000000 / t4Time:F0} ops/sec)");

        // Stress 5: Follow spamming
        Console.WriteLine("Stress Test 5: Follow Spamming (2000 follows)...");
        var t5 = Stopwatch.GetTimestamp();
        for (int i = 0; i < 2000; i++)
        {
            await MakeRequest("POST", "/api/follow", new
            {
                followerId = userIds[i % userIds.Count],
                followingId = userIds[(i + 1) % userIds.Count],
            });
        }
        var t5Time = Stopwatch.GetElapsedTime(t5).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t5Time:F0}ms ({2000000 / t5Time:F0} ops/sec)");

        var totalTime = Stopwatch.GetElapsedTime(startTime).TotalMilliseconds;

        Console.WriteLine("\n========================================");
        Console.WriteLine("           STRESS TEST RESULTS");
        Console.WriteLine("========================================");
        Console.WriteLine($"Test 1 - User Creation:      {t1Time:F0}ms");
        Console.WriteLine($"Test 2 - Post Creation:      {t2Time:F0}ms");
        Console.WriteLine($"Test 3 - Comment Addition:   {t3Time:F0}ms");
        Console.WriteLine($"Test 4 - Like Bombardment:   {t4Time:F0}ms");
        Console.WriteLine($"Test 5 - Follow Spamming:    {t5Time:F0}ms");
        Console.WriteLine($"Total Execution Time:        {totalTime:F0} ms");
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
