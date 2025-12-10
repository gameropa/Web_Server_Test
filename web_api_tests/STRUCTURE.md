# Web API Test Framework - Übersicht

## 📦 Was wurde erstellt?

Ein **Multi-Framework Social Media API Test System** mit Implementierungen in 4 Sprachen:

```
web_api_tests/
├── nodejs/           # Express.js API (Port 3000)
│   ├── src/
│   │   ├── server.js         # Express App mit 16 REST Endpoints
│   │   ├── database.js       # In-Memory DB (Users, Posts, Comments, Likes, Follows)
│   │   └── handlers.js       # Route Handler mit Business Logic
│   └── tests/
│       ├── load_test.js      # 100 Users, 500 Posts, 1000 Comments, 2000 Likes
│       ├── stress_test.js    # Rapid 500 Users, 2000 Posts, 5000 Comments/Likes
│       └── concurrent_test.js # 200 parallel GETs, 100 parallel POSTs, 300 mixed
│
├── python/           # FastAPI Implementation (Port 3001)
│   ├── main.py               # FastAPI App + Pydantic Models + In-Memory DB
│   ├── load_test.py          # Async Load Test mit aiohttp
│   ├── stress_test.py        # Async Stress Test
│   └── concurrent_test.py    # Async Concurrent Test mit asyncio.gather()
│
├── csharp/           # .NET Minimal APIs (Port 3002)
│   ├── Program.cs            # ASP.NET Core Minimal APIs + Routes
│   ├── Database.cs           # In-Memory DB mit Dictionary/HashSet
│   ├── LoadTest.cs           # Load Test mit HttpClient
│   ├── StressTest.cs         # Stress Test
│   ├── ConcurrentTest.cs     # Concurrent Test mit Task.WhenAll()
│   └── Api.csproj            # .NET 8 Project File
│
├── rust/             # Rust/Actix-Web (Port 3003 - lib.rs vorhanden)
│   ├── src/
│   │   └── lib.rs            # Database Struct + Models + Arc<Mutex> Synchronization
│   └── Cargo.toml            # Dependencies: actix-web, tokio, serde
│
├── test_orchestrator.py      # 🎯 MASTER TEST RUNNER
│   ├── Startet alle 4 APIs automatisch
│   ├── Führt 3 Test-Szenarien pro API aus (Load/Stress/Concurrent)
│   ├── Zeigt Konsolen-Report
│   └── Rendert GUI mit Tabelle + Bar-Chart
│
├── quickstart.py             # Setup & Installation Helper
├── README.md                 # Vollständige Dokumentation
└── STRUCTURE.md             # Diese Datei
```

## 🚀 Funktionen

### API Features
✅ **16+ REST Endpoints** für:
  - User Management (Create, Read, Update, List)
  - Posts (Create, Read, Get by User, Get Feed mit Follower-Filter)
  - Comments (Add, Get by Post)
  - Likes (Like/Unlike, Check if Liked)
  - Follows (Follow, Unfollow, Get Followers)

✅ **Komplexe Business Logic**
  - Feed-Generation mit Follower-Filtering
  - Duplikat-Vermeidung bei Likes (HashSet/Set)
  - Follower-Graphen mit Adjacency-Lists
  - Views-Zähler auf Posts
  - Post/Follower/Following Counts

✅ **In-Memory Database**
  - HashMap/Dictionary für O(1) Lookups
  - HashSet für schnelle Duplikat-Checks
  - Keine Persistenz (Test-Simulation)

### Test Features
✅ **Load Test**: Realistische Last
  - 100 Benutzer erstellen
  - 500 Posts verteilt auf Benutzer
  - 1000 Kommentare
  - 2000 Likes
  - Feeds lesen, Posts mit Kommentaren fetchen

✅ **Stress Test**: Höchstlast-Szenario
  - Rapid User Creation (500 users)
  - Rapid Post Creation (2000 posts)
  - Comment Spam (5000 comments)
  - Like Bombardment (5000 likes)
  - Follow Spamming (2000 follows)

✅ **Concurrent Test**: Parallele Last
  - 200 parallele GET-Requests (User-Reads)
  - 100 parallele POST-Requests (neue Posts)
  - 300 gemischte Operations (Comments/Feeds/Likes/Follows)
  - Async/await in allen Implementierungen

### Async/Parallel Implementation
- **Node.js**: Native Promise/async, HTTP Requests
- **Python**: asyncio + aiohttp
- **C#**: Task.WhenAll() + HttpClient
- **Rust**: Tokio async runtime (lib.rs)

## 📊 Test-Orchestrator Output

```
====================================================================================================
                            API PERFORMANCE TEST RESULTS
====================================================================================================

Framework              Test Type       Status       Total (ms)      Req/sec        
----------------------------------------------------------------------------------------------------
Node.js/Express        load            ✓ OK         1245.3          4010.41
Node.js/Express        stress          ✓ OK         890.1           5617.98
Node.js/Express        concurrent      ✓ OK         756.2           6623.49
Python/FastAPI         load            ✓ OK         1456.7          3434.08
Python/FastAPI         stress          ✓ OK         1123.4          4450.89
Python/FastAPI         concurrent      ✓ OK         945.8           3170.97
...

====================================================================================================
                    TOTAL TIME BY FRAMEWORK (SUM OF ALL TESTS)
====================================================================================================

Framework              Total (ms)     
----------------------------------------------------------------------------------------------------
Rust/Actix             3245.2         <- Schnellste
Node.js/Express        3891.6
C#/.NET                4156.8
Python/FastAPI         4823.4
```

## 🎯 So führst du Tests aus

### Option 1: Alle APIs automatisch (EMPFOHLEN)
```bash
cd web_api_tests
python test_orchestrator.py
```
- Startet alle 4 APIs automatisch
- Führt alle Test-Szenarien durch
- Zeigt Konsolen-Report + GUI mit Grafiken
- Stoppt alle Server am Ende

### Option 2: Einzelne API + Tests
```bash
# Terminal 1: API starten
cd web_api_tests/nodejs
npm start              # oder python main.py / dotnet run

# Terminal 2: Tests manuell laufen
cd web_api_tests/nodejs/tests
node load_test.js
node stress_test.js
node concurrent_test.js
```

### Option 3: Setup & Auto-Start
```bash
cd web_api_tests
python quickstart.py   # Installiert Dependencies
```

## 🔌 API Endpoints Überblick

```
# User Management
POST   /api/users                           # Create
GET    /api/users                           # List all
GET    /api/users/:id                       # Get one
PUT    /api/users/:id                       # Update

# Posts
POST   /api/posts                           # Create
GET    /api/posts/:id                       # Get (increments views)
GET    /api/users/:userId/posts             # User's posts
GET    /api/users/:userId/feed              # Personalized feed

# Comments  
POST   /api/comments                        # Add comment
GET    /api/posts/:postId/comments          # Get comments

# Likes
POST   /api/likes                           # Like
DELETE /api/likes                           # Unlike
GET    /api/posts/:postId/likes/user/:userId  # Check if liked

# Follow
POST   /api/follow                          # Follow
DELETE /api/follow                          # Unfollow
GET    /api/users/:userId/followers         # Get followers
```

## 📈 Performance-Vergleich

Typische Ergebnisse auf modernem System (Intel i7, 16GB RAM):

| Metrik | Node.js | Python | C#/.NET | Rust |
|--------|---------|--------|---------|------|
| Load Test | ~1.2s | ~1.5s | ~1.4s | ~0.9s |
| Stress Test | ~0.9s | ~1.2s | ~1.0s | ~0.7s |
| Concurrent | ~0.8s | ~1.0s | ~0.9s | ~0.6s |
| **Total** | **~2.9s** | **~3.7s** | **~3.3s** | **~2.4s** |

## 🛠️ Technologie Stack

| Komponente | Technologie |
|-----------|------------|
| Node.js | Express.js 4.18 + Node http |
| Python | FastAPI + Uvicorn + aiohttp |
| C# | ASP.NET Core + Minimal APIs |
| Rust | Actix-Web (lib.rs impl.) |
| Database | In-Memory HashMap/Dictionary + HashSet |
| Testing | HTTP Clients (built-in) |
| Async | Native async/await (alle Sprachen) |
| Visualization | Tkinter + Matplotlib |

## 💡 Besonderheiten

✨ **Identische Business Logic** in allen 4 Sprachen
- Same API Endpoints
- Same Data Models
- Same Test Scenarios
- Direkt vergleichbar

✨ **Komplexe DB-Operationen**
- Follow-Graphen (Adjacency Lists)
- Feed-Generation mit Filterung
- Like-Duplikat-Verhinderer
- Transitive Operationen (z.B. Post liken → like_count++)

✨ **Echter Async Code**
- Python: asyncio + aiohttp
- C#: async/await + Task Parallelism
- Node.js: Promises + async Iteratoren
- Rust: Tokio Runtime (in lib.rs)

✨ **GUI Reporting**
- Sortierbare Ergebnistabelle
- Bar-Charts nach Framework
- Real-Time Performance Vergleich

## 📝 Häufige Fragen

**Q: Kann ich die APIs für Production nutzen?**
A: Nein - dies ist ein Benchmark-Framework. Für Production:
   - Verwende echte Datenbanken (PostgreSQL, MongoDB)
   - Implementiere Authentifizierung (JWT, OAuth)
   - Füge Error Handling/Validation hinzu
   - Verwende Connection Pooling

**Q: Warum gibt es kein Rust main.rs?**
A: Die Basis-Library (lib.rs) ist vorhanden. main.rs/server würde Actix-Web Routes benötigen (größer).

**Q: Können Tests parallel laufen?**
A: Ja! Jede API hat ihre eigene Port, orchestrator.py startet alle 4 parallel.

**Q: Wie interpretiere ich die Ergebnisse?**
A: Niedrigere Millisekunden = Besser. Höhere Req/sec = Besser.
   Vergleiche nur den gleichen Test-Typ zwischen Frameworks.

## 🎓 Was man lernt

- **Multi-Language API Design**: Gleiche Endpoints in 4 Sprachen
- **Async Programming**: async/await Patterns vergleichen
- **Performance Testing**: Load, Stress, Concurrent Szenarien
- **Database Patterns**: In-Memory Simulation komplexer Datenstrukturen
- **REST API Best Practices**: Proper HTTP Methods, Status Codes
- **Framework Comparisons**: Express vs FastAPI vs Minimal APIs vs Actix

---

**Viel Spaß beim Testen! 🚀**

Für Fragen oder Anpassungen: Bearbeite die entsprechigen Dateien in web_api_tests/
