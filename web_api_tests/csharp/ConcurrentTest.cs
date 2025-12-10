using System;
using System.Net.Http;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Diagnostics;

class ConcurrentTest
{
    private static readonly string BASE_URL = "http://localhost:3002";
    private static readonly HttpClient client = new();

    static async Task Main()
    {
        Console.WriteLine("\n========================================");
        Console.WriteLine("  C#/.NET - CONCURRENT TEST");
        Console.WriteLine("========================================\n");

        var startTime = Stopwatch.GetTimestamp();

        // Setup data
        Console.WriteLine("Setting up test data...");
        var userIds = new List<int>();
        for (int i = 0; i < 50; i++)
        {
            var res = await MakeRequest("POST", "/api/users", new
            {
                username = $"concurrent{i}",
                email = $"concurrent{i}@example.com",
                displayName = $"Concurrent User {i}",
            });
            if (res != null && res.ContainsKey("id"))
                userIds.Add((int)(long)res["id"]);
        }

        var postIds = new List<int>();
        for (int i = 0; i < 100; i++)
        {
            var res = await MakeRequest("POST", "/api/posts", new
            {
                userId = userIds[i % userIds.Count],
                content = $"Post {i}",
            });
            if (res != null && res.ContainsKey("id"))
                postIds.Add((int)(long)res["id"]);
        }

        // Concurrent Test 1: Parallel reads
        Console.WriteLine("Concurrent Test 1: Parallel Reads (200 simultaneous GETs)...");
        var t1 = Stopwatch.GetTimestamp();
        var tasks1 = new List<Task>();
        for (int i = 0; i < 200; i++)
        {
            tasks1.Add(client.GetAsync($"{BASE_URL}/api/users/{userIds[i % userIds.Count]}"));
        }
        await Task.WhenAll(tasks1);
        var t1Time = Stopwatch.GetElapsedTime(t1).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t1Time:F0}ms");

        // Concurrent Test 2: Parallel writes
        Console.WriteLine("Concurrent Test 2: Parallel Writes (100 simultaneous POSTs)...");
        var t2 = Stopwatch.GetTimestamp();
        var tasks2 = new List<Task>();
        for (int i = 0; i < 100; i++)
        {
            tasks2.Add(MakeRequest("POST", "/api/posts", new
            {
                userId = userIds[i % userIds.Count],
                content = $"Concurrent post {i}",
            }));
        }
        await Task.WhenAll(tasks2);
        var t2Time = Stopwatch.GetElapsedTime(t2).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t2Time:F0}ms");

        // Concurrent Test 3: Mixed operations
        Console.WriteLine("Concurrent Test 3: Mixed Operations (300 mixed requests)...");
        var t3 = Stopwatch.GetTimestamp();
        var tasks3 = new List<Task>();
        for (int i = 0; i < 300; i++)
        {
            int op = i % 4;
            if (op == 0)
            {
                tasks3.Add(MakeRequest("POST", "/api/comments", new
                {
                    postId = postIds[i % postIds.Count],
                    userId = userIds[i % userIds.Count],
                    text = $"Mixed comment {i}",
                }));
            }
            else if (op == 1)
            {
                tasks3.Add(client.GetAsync($"{BASE_URL}/api/users/{userIds[i % userIds.Count]}/feed"));
            }
            else if (op == 2)
            {
                tasks3.Add(MakeRequest("POST", "/api/likes", new
                {
                    postId = postIds[i % postIds.Count],
                    userId = userIds[i % userIds.Count],
                }));
            }
            else
            {
                tasks3.Add(MakeRequest("POST", "/api/follow", new
                {
                    followerId = userIds[i % userIds.Count],
                    followingId = userIds[(i + 1) % userIds.Count],
                }));
            }
        }
        await Task.WhenAll(tasks3);
        var t3Time = Stopwatch.GetElapsedTime(t3).TotalMilliseconds;
        Console.WriteLine($"  ✓ Completed in {t3Time:F0}ms");

        var totalTime = Stopwatch.GetElapsedTime(startTime).TotalMilliseconds;

        Console.WriteLine("\n========================================");
        Console.WriteLine("         CONCURRENT TEST RESULTS");
        Console.WriteLine("========================================");
        Console.WriteLine($"Test 1 - Parallel Reads:     {t1Time:F0}ms");
        Console.WriteLine($"Test 2 - Parallel Writes:    {t2Time:F0}ms");
        Console.WriteLine($"Test 3 - Mixed Operations:   {t3Time:F0}ms");
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
