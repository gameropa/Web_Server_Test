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

async function runStressTest() {
  console.log("\n========================================");
  console.log("  NODE.JS/EXPRESS - STRESS TEST");
  console.log("========================================\n");

  const startTime = Date.now();

  // Stress 1: Rapid user creation
  console.log("Stress Test 1: Rapid User Creation (500 users)...");
  const t1 = Date.now();
  const userIds = [];
  for (let i = 0; i < 500; i++) {
    const res = await makeRequest("POST", "/api/users", {
      username: `stressuser${i}`,
      email: `stressuser${i}@example.com`,
      displayName: `Stress User ${i}`,
    });
    userIds.push(res.data.id);
  }
  const t1_time = Date.now() - t1;
  console.log(`  ✓ Completed in ${t1_time}ms (${(500000 / t1_time).toFixed(0)} ops/sec)`);

  // Stress 2: Rapid post creation
  console.log("Stress Test 2: Rapid Post Creation (2000 posts)...");
  const t2 = Date.now();
  const postIds = [];
  for (let i = 0; i < 2000; i++) {
    const userId = userIds[i % userIds.length];
    const res = await makeRequest("POST", "/api/posts", {
      userId,
      content: `Stress post ${i}`,
    });
    postIds.push(res.data.id);
  }
  const t2_time = Date.now() - t2;
  console.log(`  ✓ Completed in ${t2_time}ms (${(2000000 / t2_time).toFixed(0)} ops/sec)`);

  // Stress 3: Massive comment spam
  console.log("Stress Test 3: Massive Comment Addition (5000 comments)...");
  const t3 = Date.now();
  for (let i = 0; i < 5000; i++) {
    const postId = postIds[i % postIds.length];
    const userId = userIds[i % userIds.length];
    await makeRequest("POST", "/api/comments", {
      postId,
      userId,
      text: `Spam comment ${i}`,
    });
  }
  const t3_time = Date.now() - t3;
  console.log(`  ✓ Completed in ${t3_time}ms (${(5000000 / t3_time).toFixed(0)} ops/sec)`);

  // Stress 4: Like bombardment
  console.log("Stress Test 4: Like Bombardment (5000 likes)...");
  const t4 = Date.now();
  for (let i = 0; i < 5000; i++) {
    const postId = postIds[i % postIds.length];
    const userId = userIds[i % userIds.length];
    await makeRequest("POST", "/api/likes", { postId, userId }).catch(() => {});
  }
  const t4_time = Date.now() - t4;
  console.log(`  ✓ Completed in ${t4_time}ms (${(5000000 / t4_time).toFixed(0)} ops/sec)`);

  // Stress 5: Follow spamming
  console.log("Stress Test 5: Follow Spamming (2000 follows)...");
  const t5 = Date.now();
  for (let i = 0; i < 2000; i++) {
    const followerId = userIds[i % userIds.length];
    const followingId = userIds[(i + 1) % userIds.length];
    await makeRequest("POST", "/api/follow", { followerId, followingId }).catch(() => {});
  }
  const t5_time = Date.now() - t5;
  console.log(`  ✓ Completed in ${t5_time}ms (${(2000000 / t5_time).toFixed(0)} ops/sec)`);

  const totalTime = Date.now() - startTime;

  console.log("\n========================================");
  console.log("           STRESS TEST RESULTS");
  console.log("========================================");
  console.log(`Test 1 - User Creation:      ${t1_time}ms`);
  console.log(`Test 2 - Post Creation:      ${t2_time}ms`);
  console.log(`Test 3 - Comment Addition:   ${t3_time}ms`);
  console.log(`Test 4 - Like Bombardment:   ${t4_time}ms`);
  console.log(`Test 5 - Follow Spamming:    ${t5_time}ms`);
  console.log(`Total Execution Time:        ${totalTime} ms`);
  console.log("========================================\n");

  process.exit(0);
}

runStressTest().catch((err) => {
  console.error("Stress test failed:", err);
  process.exit(1);
});
