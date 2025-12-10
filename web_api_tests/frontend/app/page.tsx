"use client";

import { useMemo, useState } from "react";

type ServerKey = "node" | "python" | "csharp";

type ServerInfo = {
  name: string;
  url: string;
  accent: string;
};

type ApiLog = {
  server: string;
  endpoint: string;
  status: number;
  ok: boolean;
  duration: number;
  payload?: unknown;
  response: unknown;
};

const servers: Record<ServerKey, ServerInfo> = {
  node: {
    name: "Node.js / Express",
    url: process.env.NEXT_PUBLIC_NODE_API || "http://localhost:3000",
    accent: "#6ee7ff",
  },
  python: {
    name: "Python / FastAPI",
    url: process.env.NEXT_PUBLIC_PY_API || "http://localhost:3001",
    accent: "#fbbf24",
  },
  csharp: {
    name: "C# / .NET",
    url: process.env.NEXT_PUBLIC_CS_API || "http://localhost:3002",
    accent: "#a78bfa",
  },
};

export default function Page() {
  const [selected, setSelected] = useState<ServerKey>("python");
  const [log, setLog] = useState<ApiLog[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [healthState, setHealthState] = useState<Record<ServerKey, string>>({
    node: "unknown",
    python: "unknown",
    csharp: "unknown",
  });

  const [userForm, setUserForm] = useState({
    username: "demo",
    email: "demo@example.com",
    displayName: "Demo User",
  });

  const [postForm, setPostForm] = useState({
    userId: "1",
    content: "Hello from the unified dashboard!",
  });

  const [feedUserId, setFeedUserId] = useState("1");
  const [commentForm, setCommentForm] = useState({
    postId: "1",
    userId: "1",
    text: "Nice post!",
  });

  const active = useMemo(() => servers[selected], [selected]);

  async function callApi(
    action: string,
    method: "GET" | "POST" | "PUT" | "DELETE",
    path: string,
    body?: Record<string, unknown>
  ) {
    setLoading(action);
    const endpoint = `${active.url}${path}`;
    const started = performance.now();
    try {
      const res = await fetch(endpoint, {
        method,
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
      });
      const duration = performance.now() - started;
      const data = await res
        .json()
        .catch(() => ({ message: "No JSON returned" } as unknown));

      const entry: ApiLog = {
        server: active.name,
        endpoint: path,
        status: res.status,
        ok: res.ok,
        duration,
        payload: body,
        response: data,
      };
      setLog((prev) => [entry, ...prev].slice(0, 14));
      return entry;
    } catch (error) {
      const duration = performance.now() - started;
      const entry: ApiLog = {
        server: active.name,
        endpoint: path,
        status: 0,
        ok: false,
        duration,
        payload: body,
        response: (error as Error).message,
      };
      setLog((prev) => [entry, ...prev].slice(0, 14));
      return entry;
    } finally {
      setLoading(null);
    }
  }

  async function handleHealth(serverKey: ServerKey) {
    setLoading(`health-${serverKey}`);
    const info = servers[serverKey];
    const endpoint = `${info.url}/health`;
    const started = performance.now();
    try {
      const res = await fetch(endpoint);
      const duration = performance.now() - started;
      const data = await res.json().catch(() => ({}));
      setLog((prev) => [
        {
          server: info.name,
          endpoint: "/health",
          status: res.status,
          ok: res.ok,
          duration,
          response: data,
        },
        ...prev,
      ].slice(0, 14));
      setHealthState((prev) => ({
        ...prev,
        [serverKey]: res.ok ? "ok" : "error",
      }));
    } catch (err) {
      setHealthState((prev) => ({ ...prev, [serverKey]: "error" }));
      setLog((prev) => [
        {
          server: info.name,
          endpoint: "/health",
          status: 0,
          ok: false,
          duration: performance.now() - started,
          response: (err as Error).message,
        },
        ...prev,
      ].slice(0, 14));
    } finally {
      setLoading(null);
    }
  }

  return (
    <main>
      <section className="header">
        <p className="tagline">Unified control surface</p>
        <h1 style={{ fontSize: "34px", margin: 0 }}>
          Next.js dashboard for all three demo APIs
        </h1>
        <p className="tagline">
          Switch between Node.js, FastAPI, and C# backends; run health checks,
          create users, publish posts, and inspect feeds from one place.
        </p>
        <div className="row">
          {Object.entries(servers).map(([key, info]) => (
            <button
              key={key}
              className={`server-pill ${selected === key ? "active" : ""}`}
              style={{ borderColor: selected === key ? info.accent : undefined }}
              onClick={() => setSelected(key as ServerKey)}
            >
              <div style={{ fontWeight: 600 }}>{info.name}</div>
              <div className="server-meta">{info.url}</div>
            </button>
          ))}
        </div>
      </section>

      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="card">
          <div className="row" style={{ justifyContent: "space-between" }}>
            <h3 style={{ marginBottom: 4 }}>Health status</h3>
            <div className="row" style={{ gap: 8 }}>
              {(Object.keys(servers) as ServerKey[]).map((key) => (
                <button
                  key={key}
                  onClick={() => handleHealth(key)}
                  disabled={loading === `health-${key}`}
                >
                  {loading === `health-${key}` ? "Checking..." : `Ping ${servers[key].name}`}
                </button>
              ))}
            </div>
          </div>
          <div className="row" style={{ gap: 12 }}>
            {(Object.keys(servers) as ServerKey[]).map((key) => {
              const state = healthState[key];
              return (
                <div key={key} className="server-pill" style={{ flex: 1 }}>
                  <div className={`status ${state === "ok" ? "ok" : state === "error" ? "error" : "warn"}`}>
                    <span className="status-dot" />
                    <span>{servers[key].name}</span>
                  </div>
                  <div className="server-meta">{servers[key].url}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Active backend</h3>
          <div className="status ok" style={{ marginBottom: 12 }}>
            <span className="status-dot" style={{ background: active.accent }} />
            <span>{active.name}</span>
          </div>
          <p className="server-meta" style={{ marginBottom: 12 }}>
            Requests below will target this backend. Change selection in the pill
            row above to switch.
          </p>
          <button
            className="primary"
            onClick={() => handleHealth(selected)}
            disabled={loading === `health-${selected}`}
          >
            {loading === `health-${selected}` ? "Pinging..." : "Ping selected"}
          </button>
        </div>
      </div>

      <div className="grid" style={{ marginTop: 18, gridTemplateColumns: "2fr 1fr" }}>
        <div className="card">
          <h3>Actions</h3>
          <div className="controls">
            <div>
              <h4>Create user</h4>
              <label>Username</label>
              <input
                value={userForm.username}
                onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
              />
              <label>Email</label>
              <input
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
              />
              <label>Display name</label>
              <input
                value={userForm.displayName}
                onChange={(e) => setUserForm({ ...userForm, displayName: e.target.value })}
              />
              <button
                style={{ marginTop: 10 }}
                className="primary"
                disabled={loading === "create-user"}
                onClick={() =>
                  callApi("create-user", "POST", "/api/users", {
                    username: userForm.username,
                    email: userForm.email,
                    displayName: userForm.displayName,
                  })
                }
              >
                {loading === "create-user" ? "Creating..." : "Create user"}
              </button>
            </div>

            <div>
              <h4>Create post</h4>
              <label>User ID</label>
              <input
                value={postForm.userId}
                onChange={(e) => setPostForm({ ...postForm, userId: e.target.value })}
              />
              <label>Content</label>
              <textarea
                value={postForm.content}
                onChange={(e) => setPostForm({ ...postForm, content: e.target.value })}
              />
              <button
                style={{ marginTop: 10 }}
                className="primary"
                disabled={loading === "create-post"}
                onClick={() =>
                  callApi("create-post", "POST", "/api/posts", {
                    userId: Number(postForm.userId) || 0,
                    content: postForm.content,
                  })
                }
              >
                {loading === "create-post" ? "Publishing..." : "Publish post"}
              </button>
            </div>

            <div>
              <h4>Fetch feed</h4>
              <label>User ID</label>
              <input
                value={feedUserId}
                onChange={(e) => setFeedUserId(e.target.value)}
              />
              <label>Limit</label>
              <input value="20" disabled />
              <button
                style={{ marginTop: 10 }}
                disabled={loading === "feed"}
                onClick={() =>
                  callApi("feed", "GET", `/api/users/${feedUserId || 0}/feed?limit=20`)
                }
              >
                {loading === "feed" ? "Loading feed..." : "Load feed"}
              </button>
            </div>

            <div>
              <h4>Add comment</h4>
              <label>Post ID</label>
              <input
                placeholder="1"
                value={commentForm.postId}
                onChange={(e) => setCommentForm({ ...commentForm, postId: e.target.value })}
              />
              <label>User ID</label>
              <input
                placeholder="1"
                value={commentForm.userId}
                onChange={(e) => setCommentForm({ ...commentForm, userId: e.target.value })}
              />
              <label>Text</label>
              <textarea
                placeholder="Nice post!"
                value={commentForm.text}
                onChange={(e) => setCommentForm({ ...commentForm, text: e.target.value })}
              />
              <button
                style={{ marginTop: 10 }}
                disabled={loading === "comment"}
                onClick={() =>
                  callApi("comment", "POST", "/api/comments", {
                    postId: Number(commentForm.postId) || 0,
                    userId: Number(commentForm.userId) || 0,
                    text: commentForm.text,
                  })
                }
              >
                {loading === "comment" ? "Posting..." : "Add comment"}
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Recent responses</h3>
          {log.length === 0 && <p className="server-meta">No requests yet.</p>}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {log.map((entry, idx) => (
              <div key={`${entry.endpoint}-${idx}`} className="card" style={{ padding: 12 }}>
                <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                  <div className="status ok" style={{ gap: 8 }}>
                    <span className="status-dot" style={{ background: entry.ok ? "#6ee7a6" : "#ff7b7b" }} />
                    <strong>{entry.server}</strong>
                  </div>
                  <span className="server-meta">{entry.duration.toFixed(1)} ms</span>
                </div>
                <div className="server-meta">{entry.endpoint} · {entry.status}</div>
                {entry.payload && (
                  <details style={{ marginTop: 6 }}>
                    <summary className="server-meta">Payload</summary>
                    <pre>{JSON.stringify(entry.payload, null, 2)}</pre>
                  </details>
                )}
                <details style={{ marginTop: 6 }} open={idx === 0}>
                  <summary className="server-meta">Response</summary>
                  <pre>{JSON.stringify(entry.response, null, 2)}</pre>
                </details>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="footer-note">
        Tip: run `.\\Start-APIs.ps1` to start the backends, then `npm install` and
        `npm run dev -- --port 3003` inside `web_api_tests/frontend` to launch
        this dashboard without clashing with the Node server. Update environment
        variables in `.env.local` if your API ports differ.
      </p>
    </main>
  );
}
