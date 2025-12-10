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

async def run_concurrent_test():
    print("\n========================================")
    print("  PYTHON/FASTAPI - CONCURRENT TEST")
    print("========================================\n")

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Setup data
        print("Setting up test data...")
        user_ids = []
        for i in range(50):
            res = await make_request(session, "POST", "/api/users", {
                "username": f"concurrent{i}",
                "email": f"concurrent{i}@example.com",
                "displayName": f"Concurrent User {i}",
            })
            user_ids.append(res["data"]["id"])

        post_ids = []
        for i in range(100):
            user_id = user_ids[i % len(user_ids)]
            res = await make_request(session, "POST", "/api/posts", {
                "userId": user_id,
                "content": f"Post {i}",
            })
            post_ids.append(res["data"]["id"])

        # Concurrent Test 1: Parallel reads
        print("Concurrent Test 1: Parallel Reads (200 simultaneous GETs)...")
        t1 = time.time()
        tasks1 = []
        for i in range(200):
            user_id = user_ids[i % len(user_ids)]
            tasks1.append(make_request(session, "GET", f"/api/users/{user_id}"))
        await asyncio.gather(*tasks1)
        t1_time = (time.time() - t1) * 1000
        print(f"  ✓ Completed in {t1_time:.0f}ms")

        # Concurrent Test 2: Parallel writes
        print("Concurrent Test 2: Parallel Writes (100 simultaneous POSTs)...")
        t2 = time.time()
        tasks2 = []
        for i in range(100):
            user_id = user_ids[i % len(user_ids)]
            tasks2.append(make_request(session, "POST", "/api/posts", {
                "userId": user_id,
                "content": f"Concurrent post {i}",
            }))
        await asyncio.gather(*tasks2)
        t2_time = (time.time() - t2) * 1000
        print(f"  ✓ Completed in {t2_time:.0f}ms")

        # Concurrent Test 3: Mixed operations
        print("Concurrent Test 3: Mixed Operations (300 mixed requests)...")
        t3 = time.time()
        tasks3 = []
        for i in range(300):
            op = i % 4
            if op == 0:
                # POST comment
                tasks3.append(make_request(session, "POST", "/api/comments", {
                    "postId": post_ids[i % len(post_ids)],
                    "userId": user_ids[i % len(user_ids)],
                    "text": f"Mixed comment {i}",
                }))
            elif op == 1:
                # GET feed
                tasks3.append(make_request(session, "GET", f"/api/users/{user_ids[i % len(user_ids)]}/feed"))
            elif op == 2:
                # POST like
                tasks3.append(make_request(session, "POST", "/api/likes", {
                    "postId": post_ids[i % len(post_ids)],
                    "userId": user_ids[i % len(user_ids)],
                }))
            else:
                # POST follow
                tasks3.append(make_request(session, "POST", "/api/follow", {
                    "followerId": user_ids[i % len(user_ids)],
                    "followingId": user_ids[(i + 1) % len(user_ids)],
                }))
        await asyncio.gather(*tasks3, return_exceptions=True)
        t3_time = (time.time() - t3) * 1000
        print(f"  ✓ Completed in {t3_time:.0f}ms")

    total_time = (time.time() - start_time) * 1000

    print("\n========================================")
    print("         CONCURRENT TEST RESULTS")
    print("========================================")
    print(f"Test 1 - Parallel Reads:     {t1_time:.0f}ms")
    print(f"Test 2 - Parallel Writes:    {t2_time:.0f}ms")
    print(f"Test 3 - Mixed Operations:   {t3_time:.0f}ms")
    print(f"Total Execution Time:        {total_time:.0f} ms")
    print("========================================\n")

if __name__ == "__main__":
    asyncio.run(run_concurrent_test())
