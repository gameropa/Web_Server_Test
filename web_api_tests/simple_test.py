#!/usr/bin/env python3
"""
Simple Test Client - Tests a single API endpoint
Usage: python simple_test.py <port> <framework_name>
"""

import sys
import asyncio
import aiohttp
import time

async def test_api(port, framework):
    base_url = f"http://localhost:{port}"
    
    print(f"\n{'='*80}")
    print(f"Testing {framework} API on port {port}")
    print(f"{'='*80}\n")
    
    # Check health
    print(f"[1/5] Checking health endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✓ Server is healthy: {data}")
                else:
                    print(f"  ✗ Health check failed: {resp.status}")
                    return
    except Exception as e:
        print(f"  ✗ Cannot reach server: {e}")
        return
    
    # Quick Load Test
    print(f"\n[2/5] Creating 10 users...")
    start = time.time()
    user_ids = []
    async with aiohttp.ClientSession() as session:
        for i in range(10):
            async with session.post(f"{base_url}/api/users", json={
                "username": f"testuser{i}",
                "email": f"test{i}@example.com",
                "displayName": f"Test User {i}",
            }) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    user_ids.append(data["id"])
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Created {len(user_ids)} users in {elapsed:.1f}ms")
    
    # Create posts
    print(f"\n[3/5] Creating 20 posts...")
    start = time.time()
    post_ids = []
    async with aiohttp.ClientSession() as session:
        for i in range(20):
            async with session.post(f"{base_url}/api/posts", json={
                "userId": user_ids[i % len(user_ids)],
                "content": f"Test post #{i}",
            }) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    post_ids.append(data["id"])
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Created {len(post_ids)} posts in {elapsed:.1f}ms")
    
    # Add comments
    print(f"\n[4/5] Adding 50 comments...")
    start = time.time()
    comment_count = 0
    async with aiohttp.ClientSession() as session:
        for i in range(50):
            async with session.post(f"{base_url}/api/comments", json={
                "postId": post_ids[i % len(post_ids)],
                "userId": user_ids[i % len(user_ids)],
                "text": f"Test comment {i}",
            }) as resp:
                if resp.status == 201:
                    comment_count += 1
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Added {comment_count} comments in {elapsed:.1f}ms")
    
    # Get feed
    print(f"\n[5/5] Fetching feeds...")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        for uid in user_ids[:5]:
            async with session.get(f"{base_url}/api/users/{uid}/feed") as resp:
                if resp.status == 200:
                    data = await resp.json()
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Fetched 5 feeds in {elapsed:.1f}ms")
    
    print(f"\n{'='*80}")
    print(f"✅ Test Complete for {framework}!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_test.py <port> <framework_name>")
        print("Example: python simple_test.py 3000 'Node.js/Express'")
        sys.exit(1)
    
    port = int(sys.argv[1])
    framework = sys.argv[2]
    
    asyncio.run(test_api(port, framework))
