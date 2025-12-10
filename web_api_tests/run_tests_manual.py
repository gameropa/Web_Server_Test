#!/usr/bin/env python3
"""
Manual Test Runner - Assumes APIs are already running
Tests all available APIs on their respective ports
"""

import asyncio
import aiohttp
import time
import sys

try:
    import tkinter as tk
    from tkinter import ttk
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_GUI = True
except ImportError:
    HAS_GUI = False


class ManualTester:
    def __init__(self):
        self.results = []
        self.apis = [
            {"name": "Node.js/Express", "port": 3000},
            {"name": "Python/FastAPI", "port": 3001},
            {"name": "C#/.NET", "port": 3002},
        ]

    async def check_health(self, port, name):
        """Check if API is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    return resp.status == 200
        except:
            return False

    async def run_test(self, port, name):
        """Run quick test against API"""
        base_url = f"http://localhost:{port}"
        
        try:
            start = time.time()
            
            # Create users
            user_ids = []
            async with aiohttp.ClientSession() as session:
                for i in range(20):
                    async with session.post(f"{base_url}/api/users", json={
                        "username": f"user{i}",
                        "email": f"user{i}@example.com",
                        "displayName": f"User {i}",
                    }) as resp:
                        if resp.status == 201:
                            data = await resp.json()
                            user_ids.append(data["id"])
            
            # Create posts
            post_ids = []
            async with aiohttp.ClientSession() as session:
                for i in range(50):
                    async with session.post(f"{base_url}/api/posts", json={
                        "userId": user_ids[i % len(user_ids)],
                        "content": f"Post {i}",
                    }) as resp:
                        if resp.status == 201:
                            data = await resp.json()
                            post_ids.append(data["id"])
            
            # Add comments
            async with aiohttp.ClientSession() as session:
                for i in range(100):
                    async with session.post(f"{base_url}/api/comments", json={
                        "postId": post_ids[i % len(post_ids)],
                        "userId": user_ids[i % len(user_ids)],
                        "text": f"Comment {i}",
                    }) as resp:
                        pass
            
            # Like posts
            async with aiohttp.ClientSession() as session:
                for i in range(100):
                    async with session.post(f"{base_url}/api/likes", json={
                        "postId": post_ids[i % len(post_ids)],
                        "userId": user_ids[(i + 1) % len(user_ids)],
                    }) as resp:
                        pass
            
            # Get feeds
            async with aiohttp.ClientSession() as session:
                for uid in user_ids:
                    async with session.get(f"{base_url}/api/users/{uid}/feed") as resp:
                        pass
            
            total_ms = (time.time() - start) * 1000
            return {"status": "✓ OK", "time": total_ms, "error": None}
            
        except Exception as e:
            return {"status": "✗ FAIL", "time": None, "error": str(e)}

    async def run_all_tests(self):
        """Run tests against all APIs"""
        print("\n" + "="*80)
        print("TESTING RUNNING APIs".center(80))
        print("="*80 + "\n")
        
        for api in self.apis:
            name = api["name"]
            port = api["port"]
            
            print(f"[{name}] Checking if running on port {port}...")
            
            is_healthy = await self.check_health(port, name)
            
            if not is_healthy:
                print(f"  ⚠ {name} not running on port {port} - SKIP")
                self.results.append({
                    "name": name,
                    "status": "SKIP",
                    "time": None,
                    "error": "Server not running"
                })
                continue
            
            print(f"  ✓ {name} is running, executing test...")
            result = await self.run_test(port, name)
            
            self.results.append({
                "name": name,
                "status": result["status"],
                "time": result["time"],
                "error": result["error"]
            })
            
            if result["status"] == "✓ OK":
                print(f"  ✓ Test completed in {result['time']:.1f}ms")
            else:
                print(f"  ✗ Test failed: {result['error']}")
        
        self.print_report()
        
        if HAS_GUI:
            self.render_gui()

    def print_report(self):
        """Print console report"""
        print("\n" + "="*80)
        print("TEST RESULTS".center(80))
        print("="*80)
        print(f"\n{'Framework':<25} {'Status':<15} {'Time (ms)':<15}")
        print("-"*80)
        
        for r in self.results:
            time_str = f"{r['time']:.1f}" if r['time'] else "n/a"
            print(f"{r['name']:<25} {r['status']:<15} {time_str:<15}")
        
        # Calculate average
        valid_times = [r['time'] for r in self.results if r['time']]
        if valid_times:
            avg = sum(valid_times) / len(valid_times)
            print(f"\nAverage time: {avg:.1f}ms")
        
        print("="*80 + "\n")

    def render_gui(self):
        """Render GUI with results"""
        root = tk.Tk()
        root.title("API Test Results")
        root.geometry("800x600")
        
        # Table
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Test Results", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)
        
        cols = ("Framework", "Status", "Time (ms)")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for r in self.results:
            time_str = f"{r['time']:.1f}" if r['time'] else "n/a"
            tree.insert("", tk.END, values=(r['name'], r['status'], time_str))
        
        # Chart
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        names = [r['name'] for r in self.results if r['time']]
        times = [r['time'] for r in self.results if r['time']]
        
        if names and times:
            ax.bar(names, times, color=['#4ECDC4', '#FF6B6B', '#45B7D1'])
            ax.set_ylabel("Time (ms)")
            ax.set_title("API Performance Comparison")
            ax.tick_params(axis='x', rotation=45)
        
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10)
        
        root.mainloop()


async def main():
    tester = ManualTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("\n⚠ Make sure APIs are running before starting tests!")
    print("Run: .\\Start-APIs.ps1 in a separate terminal first\n")
    
    input("Press ENTER to start tests...")
    
    asyncio.run(main())
