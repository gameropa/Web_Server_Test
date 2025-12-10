import http from "http";

const BASE_URL = "http://localhost:3000";

async function makeRequest(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        resolve({
          status: res.statusCode,
          data: data ? JSON.parse(data) : null,
        });
      });
    });

    req.on("error", reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function runLoadTest() {
  console.log("\n========================================");
  console.log("  NODE.JS/EXPRESS - LOAD TEST");
  console.log("========================================\n");

  const startTime = Date.now();

  // Create users
  console.log("Creating 100 users...");
  const userIds = [];
  for (let i = 0; i < 100; i++) {
    const res = await makeRequest("POST", "/api/users", {
      username: `user${i}`,
      email: `user${i}@example.com`,
      displayName: `User ${i}`,
    });
    userIds.push(res.data.id);
  }

  // Create posts
  console.log("Creating 500 posts...");
  const postIds = [];
  for (let i = 0; i < 500; i++) {
    const userId = userIds[i % userIds.length];
    const res = await makeRequest("POST", "/api/posts", {
      userId,
      content: `Post #${i} - Lorem ipsum dolor sit amet`,
    });
    postIds.push(res.data.id);
  }

  // Add comments
  console.log("Adding 1000 comments...");
  for (let i = 0; i < 1000; i++) {
    const postId = postIds[i % postIds.length];
    const userId = userIds[i % userIds.length];
    await makeRequest("POST", "/api/comments", {
      postId,
      userId,
      text: `Comment #${i} - Great post!`,
    });
  }

  // Like posts
  console.log("Liking 2000 times...");
  let likeCount = 0;
  for (let i = 0; i < 2000; i++) {
    const postId = postIds[i % postIds.length];
    const userId = userIds[(i + 1) % userIds.length];
    const res = await makeRequest("POST", "/api/likes", { postId, userId });
    if (res.status === 201) likeCount++;
  }

  // Follow users
  console.log("Creating 500 follow relationships...");
  let followCount = 0;
  for (let i = 0; i < 500; i++) {
    const followerId = userIds[i % userIds.length];
    const followingId = userIds[(i + 1) % userIds.length];
    const res = await makeRequest("POST", "/api/follow", {
      followerId,
      followingId,
    });
    if (res.status === 201) followCount++;
  }

  // Fetch feeds
  console.log("Fetching 100 feeds...");
  for (let i = 0; i < 100; i++) {
    await makeRequest("GET", `/api/users/${userIds[i]}/feed`);
  }

  // Fetch posts with comments
  console.log("Fetching posts with comments...");
  for (let i = 0; i < 100; i++) {
    await makeRequest("GET", `/api/posts/${postIds[i]}`);
    await makeRequest("GET", `/api/posts/${postIds[i]}/comments`);
  }

  const totalTime = Date.now() - startTime;

  console.log("\n========================================");
  console.log("           LOAD TEST RESULTS");
  console.log("========================================");
  console.log(`Users Created:        100`);
  console.log(`Posts Created:        500`);
  console.log(`Comments Added:       1000`);
  console.log(`Likes Successful:     ${likeCount}`);
  console.log(`Follows Successful:   ${followCount}`);
  console.log(`Total Execution Time: ${totalTime} ms`);
  console.log(`Requests/sec:         ${((5000 * 1000) / totalTime).toFixed(2)}`);
  console.log("========================================\n");

  process.exit(0);
}

runLoadTest().catch((err) => {
  console.error("Load test failed:", err);
  process.exit(1);
});
