#!/usr/bin/env python3
"""
Global API Test Orchestrator
Tests multiple Social Media API implementations across different frameworks/languages
"""

import subprocess
import asyncio
import aiohttp
import time
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class APITestResult:
    framework: str
    test_type: str  # "load", "stress", "concurrent"
    total_ms: Optional[float]
    status: str
    output: str
    requests_per_sec: Optional[float] = None


class APITester:
    def __init__(self):
        self.results: List[APITestResult] = []
        self.servers = [
            {"name": "Node.js/Express", "port": 3000, "dir": ROOT / "web_api_tests" / "nodejs"},
            {"name": "Python/FastAPI", "port": 3001, "dir": ROOT / "web_api_tests" / "python"},
            {"name": "C#/.NET", "port": 3002, "dir": ROOT / "web_api_tests" / "csharp"},
            {"name": "Rust/Actix", "port": 3003, "dir": ROOT / "web_api_tests" / "rust"},
        ]
        self.processes = {}

    def start_servers(self):
        """Start all API servers"""
        print("\n" + "=" * 80)
        print("STARTING API SERVERS".center(80))
        print("=" * 80 + "\n")

        # Node.js
        print("[1/4] Starting Node.js/Express server...")
        try:
            proc = subprocess.Popen(
                ["node", "src/server.js"],
                cwd=str(self.servers[0]["dir"]),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
            self.processes["Node.js"] = proc
            print("  ✓ Node.js running on port 3000")
            time.sleep(2)
        except Exception as e:
            print(f"  ✗ Failed: {e}")

        # Python
        print("[2/4] Starting Python/FastAPI server...")
        try:
            proc = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=str(self.servers[1]["dir"]),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
            self.processes["Python"] = proc
            print("  ✓ Python running on port 3001")
            time.sleep(3)
        except Exception as e:
            print(f"  ✗ Failed: {e}")

        # C#
        print("[3/4] Starting C#/.NET server...")
        try:
            proc = subprocess.Popen(
                ["dotnet", "run", "-c", "Release"],
                cwd=str(self.servers[2]["dir"]),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
            self.processes["C#"] = proc
            print("  ✓ C# running on port 3002")
            time.sleep(3)
        except Exception as e:
            print(f"  ✗ Failed: {e}")

        # Rust - Optional (kann fehlen, ist ok)
        print("[4/4] Starting Rust/Actix server (optional)...")
        try:
            proc = subprocess.Popen(
                ["cargo", "run", "--release", "--bin", "server"],
                cwd=str(self.servers[3]["dir"]),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            )
            self.processes["Rust"] = proc
            print("  ✓ Rust running on port 3003")
            time.sleep(3)
        except Exception as e:
            print(f"  ⚠ Rust startup skipped (optional): {e}")

    async def run_test(self, framework: str, port: int, test_type: str):
        """Run a test against an API server"""
        base_url = f"http://localhost:{port}"
        max_retries = 5
        
        # Wait for server to be ready
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            break
            except:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start = time.time()

                if test_type == "load":
                    await self._load_test(session, base_url, framework)
                elif test_type == "stress":
                    await self._stress_test(session, base_url, framework)
                elif test_type == "concurrent":
                    await self._concurrent_test(session, base_url, framework)

                total_ms = (time.time() - start) * 1000
                status = "✓ OK"
                output = f"{framework} {test_type} test completed"
                rps = (5000 * 1000 / total_ms) if total_ms > 0 else 0

                result = APITestResult(
                    framework=framework,
                    test_type=test_type,
                    total_ms=total_ms,
                    status=status,
                    output=output,
                    requests_per_sec=rps,
                )
                self.results.append(result)

        except Exception as e:
            result = APITestResult(
                framework=framework,
                test_type=test_type,
                total_ms=None,
                status="✗ FAIL",
                output=str(e),
            )
            self.results.append(result)

    async def _load_test(self, session, base_url, framework):
        """Simulate load test: 100 users, 500 posts, 1000 comments, 2000 likes"""
        user_ids = []
        for i in range(100):
            async with session.post(
                f"{base_url}/api/users",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "displayName": f"User {i}",
                },
            ) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    user_ids.append(data.get("id"))

        post_ids = []
        for i in range(500):
            user_id = user_ids[i % len(user_ids)]
            async with session.post(
                f"{base_url}/api/posts",
                json={"userId": user_id, "content": f"Post #{i}"},
            ) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    post_ids.append(data.get("id"))

        for i in range(1000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[i % len(user_ids)]
            async with session.post(
                f"{base_url}/api/comments",
                json={"postId": post_id, "userId": user_id, "text": f"Comment {i}"},
            ) as resp:
                pass

        for i in range(2000):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[(i + 1) % len(user_ids)]
            async with session.post(
                f"{base_url}/api/likes",
                json={"postId": post_id, "userId": user_id},
            ) as resp:
                pass

    async def _stress_test(self, session, base_url, framework):
        """Stress test: Rapid operations"""
        user_ids = []
        for i in range(100):
            async with session.post(
                f"{base_url}/api/users",
                json={
                    "username": f"stress{i}",
                    "email": f"stress{i}@example.com",
                    "displayName": f"Stress {i}",
                },
            ) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    user_ids.append(data.get("id"))

        # Rapid posts
        post_ids = []
        for i in range(200):
            user_id = user_ids[i % len(user_ids)]
            async with session.post(
                f"{base_url}/api/posts",
                json={"userId": user_id, "content": f"Stress post {i}"},
            ) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    post_ids.append(data.get("id"))

        # Rapid comments
        for i in range(500):
            post_id = post_ids[i % len(post_ids)]
            user_id = user_ids[i % len(user_ids)]
            async with session.post(
                f"{base_url}/api/comments",
                json={"postId": post_id, "userId": user_id, "text": f"Spam {i}"},
            ) as resp:
                pass

    async def _concurrent_test(self, session, base_url, framework):
        """Concurrent test: Parallel operations"""
        user_ids = []
        tasks = []
        for i in range(50):
            task = session.post(
                f"{base_url}/api/users",
                json={
                    "username": f"concurrent{i}",
                    "email": f"concurrent{i}@example.com",
                    "displayName": f"Concurrent {i}",
                },
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for resp in responses:
            if hasattr(resp, "status") and resp.status == 201:
                data = await resp.json()
                user_ids.append(data.get("id"))

        # Parallel reads
        tasks = [session.get(f"{base_url}/api/users/{uid}") for uid in user_ids[:20]]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Parallel writes
        tasks = []
        for i in range(50):
            user_id = user_ids[i % len(user_ids)]
            task = session.post(
                f"{base_url}/api/posts",
                json={"userId": user_id, "content": f"Concurrent post {i}"},
            )
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

    def stop_servers(self):
        """Stop all API servers"""
        print("\n" + "=" * 80)
        print("STOPPING API SERVERS".center(80))
        print("=" * 80 + "\n")
        
        for name, proc in self.processes.items():
            try:
                if sys.platform == "win32":
                    proc.terminate()
                else:
                    proc.kill()
                print(f"  ✓ Stopped {name}")
            except:
                pass

    def print_report(self):
        """Print test results to console"""
        print("\n" + "=" * 100)
        print("API PERFORMANCE TEST RESULTS".center(100))
        print("=" * 100)
        print(f"\n{'Framework':<20} {'Test Type':<15} {'Status':<12} {'Total (ms)':<15} {'Req/sec':<15}")
        print("-" * 100)

        for r in self.results:
            time_str = f"{r.total_ms:.1f}" if r.total_ms else "n/a"
            rps_str = f"{r.requests_per_sec:.0f}" if r.requests_per_sec else "n/a"
            print(f"{r.framework:<20} {r.test_type:<15} {r.status:<12} {time_str:<15} {rps_str:<15}")

        # Summary by framework
        print("\n" + "=" * 100)
        print("TOTAL TIME BY FRAMEWORK (SUM OF ALL TESTS)".center(100))
        print("=" * 100)
        
        framework_totals = {}
        for r in self.results:
            if r.total_ms:
                framework_totals.setdefault(r.framework, 0)
                framework_totals[r.framework] += r.total_ms

        print(f"\n{'Framework':<20} {'Total (ms)':<15}")
        print("-" * 100)
        for fw, total in sorted(framework_totals.items(), key=lambda x: x[1]):
            print(f"{fw:<20} {total:<15.1f}")

    def render_gui(self):
        """Render GUI with results"""
        if not HAS_GUI:
            return

        root = tk.Tk()
        root.title("API Performance Comparison")
        root.geometry("1200x700")

        # Results table
        frame_left = ttk.Frame(root)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_left, text="Test Results", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        cols = ("Framework", "Type", "Status", "Time (ms)", "Req/sec")
        tree = ttk.Treeview(frame_left, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True)

        for r in self.results:
            time_val = f"{r.total_ms:.1f}" if r.total_ms else "n/a"
            rps_val = f"{r.requests_per_sec:.0f}" if r.requests_per_sec else "n/a"
            tree.insert("", tk.END, values=(r.framework, r.test_type, r.status, time_val, rps_val))

        # Chart
        frame_right = ttk.Frame(root)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame_right, text="Performance Chart", font=("Arial", 12, "bold")).pack(anchor=tk.W)

        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        framework_totals = {}
        for r in self.results:
            if r.total_ms:
                framework_totals.setdefault(r.framework, 0)
                framework_totals[r.framework] += r.total_ms

        if framework_totals:
            frameworks = list(framework_totals.keys())
            times = [framework_totals[k] for k in frameworks]
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]
            ax.bar(frameworks, times, color=colors[:len(frameworks)])
            ax.set_ylabel("Total Time (ms)", fontsize=10)
            ax.set_title("Total Execution Time by Framework", fontsize=11, fontweight="bold")
            ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=frame_right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        root.mainloop()


async def main():
    tester = APITester()
    
    try:
        # Start servers
        tester.start_servers()
        time.sleep(2)

        # Run tests
        print("\n" + "=" * 80)
        print("RUNNING API TESTS".center(80))
        print("=" * 80 + "\n")

        # Node.js tests
        print("Testing Node.js/Express...")
        await tester.run_test("Node.js/Express", 3000, "load")
        await tester.run_test("Node.js/Express", 3000, "stress")
        await tester.run_test("Node.js/Express", 3000, "concurrent")

        # Python tests
        print("Testing Python/FastAPI...")
        await tester.run_test("Python/FastAPI", 3001, "load")
        await tester.run_test("Python/FastAPI", 3001, "stress")
        await tester.run_test("Python/FastAPI", 3001, "concurrent")

        # C# tests
        print("Testing C#/.NET...")
        await tester.run_test("C#/.NET", 3002, "load")
        await tester.run_test("C#/.NET", 3002, "stress")
        await tester.run_test("C#/.NET", 3002, "concurrent")

        # Rust tests
        print("Testing Rust/Actix...")
        await tester.run_test("Rust/Actix", 3003, "load")
        await tester.run_test("Rust/Actix", 3003, "stress")
        await tester.run_test("Rust/Actix", 3003, "concurrent")

        # Print results
        tester.print_report()

        # Show GUI
        if HAS_GUI:
            print("\nLaunching GUI...")
            tester.render_gui()

    finally:
        tester.stop_servers()


if __name__ == "__main__":
    asyncio.run(main())
