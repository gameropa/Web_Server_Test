import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:3001"

async def make_request(session, method, path, json=None):
    async with session.request(method, f"{BASE_URL}{path}", json=json) as resp:
        try:
            data = await resp.json()
        except:
            data = None
        return {"status": resp.status, "data": data}

async def run_stress_test():
    print("\n========================================")
    print("  PYTHON/FASTAPI - STRESS TEST")
    print("========================================\n")

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Stress 1: Rapid user creation
        print("Stress Test 1: Rapid User Creation (500 users)...")
        t1 = time.time()
        user_ids = []
        for i in range(500):
            res = await make_request(session, "POST", "/api/users", {
                "username": f"stressuser{i}",
                "email": f"stressuser{i}@example.com",
                "displayName": f"Stress User {i}",
            })
            user_ids.append(res["data"]["id"])
        t1_time = (time.time() - t1) * 1000
        print(f"  ✓ Completed in {t1_time:.0f}ms ({500000 / t1_time:.0f} ops/sec)")

        # Stress 2: Rapid post creation
        print("Stress Test 2: Rapid Post Creation (2000 posts)...")
        t2 = time.time()
        post_ids = []
        for i in range(2000):
            user_id = user_ids[i % len(user_ids)]
            res = await make_request(session, "POST", "/api/posts", {
                "userId": user_id,
                "content": f"Stress post {i}",
            })
            post_ids.append(res["data"]["id"])
        t2_time = (time.time() - t2) * 1000
        print(f"  ✓ Completed in {t2_time:.0f}ms ({2000000 / t2_time:.0f} ops/sec)")

        # Stress 3: Massive comment spam
        print("Stress Test 3: Massive Comment Addition (5000 comments)...")
        t3 = time.time()
        for i in range(5000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[i % len(user_ids)]
            await make_request(session, "POST", "/api/comments", {
                "postId": post_id,
                "userId": user_id,
                "text": f"Spam comment {i}",
            })
        t3_time = (time.time() - t3) * 1000
        print(f"  ✓ Completed in {t3_time:.0f}ms ({5000000 / t3_time:.0f} ops/sec)")

        # Stress 4: Like bombardment
        print("Stress Test 4: Like Bombardment (5000 likes)...")
        t4 = time.time()
        for i in range(5000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[i % len(user_ids)]
            await make_request(session, "POST", "/api/likes", {
                "postId": post_id,
                "userId": user_id,
            })
        t4_time = (time.time() - t4) * 1000
        print(f"  ✓ Completed in {t4_time:.0f}ms ({5000000 / t4_time:.0f} ops/sec)")

        # Stress 5: Follow spamming
        print("Stress Test 5: Follow Spamming (2000 follows)...")
        t5 = time.time()
        for i in range(2000):
            follower_id = user_ids[i % len(user_ids)]
            following_id = user_ids[(i + 1) % len(user_ids)]
            await make_request(session, "POST", "/api/follow", {
                "followerId": follower_id,
                "followingId": following_id,
            })
        t5_time = (time.time() - t5) * 1000
        print(f"  ✓ Completed in {t5_time:.0f}ms ({2000000 / t5_time:.0f} ops/sec)")

    total_time = (time.time() - start_time) * 1000

    print("\n========================================")
    print("           STRESS TEST RESULTS")
    print("========================================")
    print(f"Test 1 - User Creation:      {t1_time:.0f}ms")
    print(f"Test 2 - Post Creation:      {t2_time:.0f}ms")
    print(f"Test 3 - Comment Addition:   {t3_time:.0f}ms")
    print(f"Test 4 - Like Bombardment:   {t4_time:.0f}ms")
    print(f"Test 5 - Follow Spamming:    {t5_time:.0f}ms")
    print(f"Total Execution Time:        {total_time:.0f} ms")
    print("========================================\n")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
