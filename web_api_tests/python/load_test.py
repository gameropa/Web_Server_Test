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

async def run_load_test():
    print("\n========================================")
    print("  PYTHON/FASTAPI - LOAD TEST")
    print("========================================\n")

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Create users
        print("Creating 100 users...")
        user_ids = []
        for i in range(100):
            res = await make_request(session, "POST", "/api/users", {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "displayName": f"User {i}",
            })
            user_ids.append(res["data"]["id"])

        # Create posts
        print("Creating 500 posts...")
        post_ids = []
        for i in range(500):
            user_id = user_ids[i % len(user_ids)]
            res = await make_request(session, "POST", "/api/posts", {
                "userId": user_id,
                "content": f"Post #{i} - Lorem ipsum dolor sit amet",
            })
            post_ids.append(res["data"]["id"])

        # Add comments
        print("Adding 1000 comments...")
        for i in range(1000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[i % len(user_ids)]
            await make_request(session, "POST", "/api/comments", {
                "postId": post_id,
                "userId": user_id,
                "text": f"Comment #{i} - Great post!",
            })

        # Like posts
        print("Liking 2000 times...")
        like_count = 0
        for i in range(2000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[(i + 1) % len(user_ids)]
            res = await make_request(session, "POST", "/api/likes", {
                "postId": post_id,
                "userId": user_id,
            })
            if res["status"] == 201:
                like_count += 1

        # Follow users
        print("Creating 500 follow relationships...")
        follow_count = 0
        for i in range(500):
            follower_id = user_ids[i % len(user_ids)]
            following_id = user_ids[(i + 1) % len(user_ids)]
            res = await make_request(session, "POST", "/api/follow", {
                "followerId": follower_id,
                "followingId": following_id,
            })
            if res["status"] == 201:
                follow_count += 1

        # Fetch feeds
        print("Fetching 100 feeds...")
        for i in range(100):
            await make_request(session, "GET", f"/api/users/{user_ids[i]}/feed")

        # Fetch posts with comments
        print("Fetching posts with comments...")
        for i in range(100):
            await make_request(session, "GET", f"/api/posts/{post_ids[i]}")
            await make_request(session, "GET", f"/api/posts/{post_ids[i]}/comments")

    total_time = (time.time() - start_time) * 1000

    print("\n========================================")
    print("           LOAD TEST RESULTS")
    print("========================================")
    print(f"Users Created:        100")
    print(f"Posts Created:        500")
    print(f"Comments Added:       1000")
    print(f"Likes Successful:     {like_count}")
    print(f"Follows Successful:   {follow_count}")
    print(f"Total Execution Time: {total_time:.0f} ms")
    print(f"Requests/sec:         {(5000 * 1000 / total_time):.2f}")
    print("========================================\n")

if __name__ == "__main__":
    asyncio.run(run_load_test())
