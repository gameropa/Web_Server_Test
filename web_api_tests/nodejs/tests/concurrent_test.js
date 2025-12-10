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

async function runConcurrentTest() {
  console.log("\n========================================");
  console.log("  NODE.JS/EXPRESS - CONCURRENT TEST");
  console.log("========================================\n");

  const startTime = Date.now();

  // Setup data
  console.log("Setting up test data...");
  const userIds = [];
  for (let i = 0; i < 50; i++) {
    const res = await makeRequest("POST", "/api/users", {
      username: `concurrent${i}`,
      email: `concurrent${i}@example.com`,
      displayName: `Concurrent User ${i}`,
    });
    userIds.push(res.data.id);
  }

  const postIds = [];
  for (let i = 0; i < 100; i++) {
    const userId = userIds[i % userIds.length];
    const res = await makeRequest("POST", "/api/posts", {
      userId,
      content: `Post ${i}`,
    });
    postIds.push(res.data.id);
  }

  // Concurrent Test 1: Parallel reads
  console.log("Concurrent Test 1: Parallel Reads (200 simultaneous GETs)...");
  const t1 = Date.now();
  const promises1 = [];
  for (let i = 0; i < 200; i++) {
    const userId = userIds[i % userIds.length];
    promises1.push(makeRequest("GET", `/api/users/${userId}`));
  }
  await Promise.all(promises1);
  const t1_time = Date.now() - t1;
  console.log(`  ✓ Completed in ${t1_time}ms`);

  // Concurrent Test 2: Parallel writes
  console.log("Concurrent Test 2: Parallel Writes (100 simultaneous POSTs)...");
  const t2 = Date.now();
  const promises2 = [];
  for (let i = 0; i < 100; i++) {
    const userId = userIds[i % userIds.length];
    promises2.push(
      makeRequest("POST", "/api/posts", {
        userId,
        content: `Concurrent post ${i}`,
      })
    );
  }
  await Promise.all(promises2);
  const t2_time = Date.now() - t2;
  console.log(`  ✓ Completed in ${t2_time}ms`);

  // Concurrent Test 3: Mixed operations
  console.log("Concurrent Test 3: Mixed Operations (300 mixed requests)...");
  const t3 = Date.now();
  const promises3 = [];
  for (let i = 0; i < 300; i++) {
    const op = i % 4;
    if (op === 0) {
      // POST comment
      promises3.push(
        makeRequest("POST", "/api/comments", {
          postId: postIds[i % postIds.length],
          userId: userIds[i % userIds.length],
          text: `Mixed comment ${i}`,
        })
      );
    } else if (op === 1) {
      // GET feed
      promises3.push(
        makeRequest("GET", `/api/users/${userIds[i % userIds.length]}/feed`)
      );
    } else if (op === 2) {
      // POST like
      promises3.push(
        makeRequest("POST", "/api/likes", {
          postId: postIds[i % postIds.length],
          userId: userIds[i % userIds.length],
        }).catch(() => {})
      );
    } else {
      // POST follow
      promises3.push(
        makeRequest("POST", "/api/follow", {
          followerId: userIds[i % userIds.length],
          followingId: userIds[(i + 1) % userIds.length],
        }).catch(() => {})
      );
    }
  }
  await Promise.all(promises3);
  const t3_time = Date.now() - t3;
  console.log(`  ✓ Completed in ${t3_time}ms`);

  const totalTime = Date.now() - startTime;

  console.log("\n========================================");
  console.log("         CONCURRENT TEST RESULTS");
  console.log("========================================");
  console.log(`Test 1 - Parallel Reads:     ${t1_time}ms`);
  console.log(`Test 2 - Parallel Writes:    ${t2_time}ms`);
  console.log(`Test 3 - Mixed Operations:   ${t3_time}ms`);
  console.log(`Total Execution Time:        ${totalTime} ms`);
  console.log("========================================\n");

  process.exit(0);
}

runConcurrentTest().catch((err) => {
  console.error("Concurrent test failed:", err);
  process.exit(1);
});
