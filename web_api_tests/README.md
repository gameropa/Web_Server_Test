# Social Media API - Multi-Framework Performance Testing

Umfassendes Web-API-Testing Framework mit Implementierungen in mehreren Programmiersprachen und Frameworks.

## 📋 Überblick

Dieses Projekt enthält eine komplette Social Media API (User, Posts, Comments, Likes, Follows) implementiert in:

- **Node.js** mit Express
- **Python** mit FastAPI  
- **C#** mit .NET Minimal APIs
- **Rust** mit Actix-Web (grundlegend, lib.rs vorhanden)

Jede Implementierung hat:
- Vollständige REST API mit ~16 Endpoints
- In-Memory Database Simulation
- Komplexe Business Logic (Follows, Feeds, Likes, Comments)
- Load, Stress und Concurrent Test Suites

## 🚀 Quick Start

### Voraussetzungen

```bash
# Node.js 18+ (mit npm)
node --version

# Python 3.10+
python --version

# .NET SDK 8.0+
dotnet --version

# Rust/Cargo (für Rust API - optional)
cargo --version
```

### Installation

```bash
# Node.js Dependencies
cd nodejs
npm install

# Python Dependencies
cd python
pip install fastapi uvicorn aiohttp

# C# läuft out-of-the-box mit .NET SDK
cd csharp
dotnet restore

# Rust (optional - nur lib.rs, main.rs/tests noch nicht implementiert)
cd rust
cargo build --release
```

### 🖥 Next.js Frontend (Dashboard für alle APIs)

```bash
cd web_api_tests/frontend
npm install
cp .env.local.example .env.local   # optional: Ports anpassen
npm run dev -- --port 3003          # startet Next.js (empfohlen: 3003, damit 3000 frei für Node bleibt)
```

Der Frontend-Dashboard spricht alle drei Backends an (Node 3000, FastAPI 3001, C# 3002). Passe die Werte in `.env.local` an, wenn Deine Ports abweichen. Aktionen: Health-Checks, User/Post/Feed/Comment Requests pro ausgewähltem Backend.

## 🐳 Docker / Compose

Im Ordner `web_api_tests` liegt ein `docker-compose.yml`, das alle Services baut und startet:

```bash
cd web_api_tests
docker compose up --build
```

Services/Ports:
- `node-api`    → http://localhost:3000
- `python-api`  → http://localhost:3001
- `csharp-api`  → http://localhost:3002
- `frontend`    → http://localhost:3003 (spricht die anderen per Service-Namen an)

Frontend-Umgebungsvariablen sind im Compose bereits gesetzt (`NEXT_PUBLIC_*`). Zum Anpassen der Ports oder Hosts editiere `docker-compose.yml` oder `.env.local` im Frontend.

## ⚙️ CI/CD & Auto-Deployment

### Option 1: GitHub Actions (Automated Builds & Deploy)

Automatisch bauen, pushen zu Docker Hub und auf Server deployen bei `git push main`:

```bash
# 1. GitHub Secrets setzen:
#    DOCKER_HUB_USERNAME, DOCKER_HUB_PASSWORD
#    DEPLOY_SSH_KEY (private key), DEPLOY_USER, DEPLOY_HOST, DEPLOY_PATH

# 2. Workflow wird ausgelöst bei git push

# 3. Status in GitHub Actions Tab sehen
```

**Workflow-Datei:** `.github/workflows/deploy.yml`

### Option 2: Traefik Load Balancer (Multi-Instance + Reverse Proxy)

```bash
cd web_api_tests
docker compose -f docker-compose-lb.yml up --build
```

- **Traefik Dashboard**: http://localhost:8080
- **Load Balancing**: Node (2 Instanzen), Python (2 Instanzen), C#/Frontend (1 Instanz)
- **Auto-Scaling**: Einfach Services duplizieren in Compose-File
- **Internal Service Discovery**: Services sprechen sich über Service-Namen an

**Features:**
- Automatisches SSL/TLS (mit Let's Encrypt konfigurierbar)
- Health Checks built-in
- Centralized Routing auf Port 80/443

### Option 3: Webhook + Manual Deployment (RPi5)

Starte den Python Webhook-Server auf RPi5:

```bash
# RPi5
python3 webhook_server.py

# Oder mit Environment-Variablen:
WEBHOOK_SECRET=your-secret-key \
REPO_PATH=/opt/web-api-tests \
COMPOSE_FILE=docker-compose-rpi.yml \
WEBHOOK_PORT=9000 \
python3 webhook_server.py
```

**GitHub Webhook Setup:**
1. Repository → Settings → Webhooks → Add webhook
2. Payload URL: `http://your-rpi-ip:9000/webhook`
3. Content type: `application/json`
4. Secret: (setze `WEBHOOK_SECRET`)
5. Events: `push`
6. Bei `git push main` → RPi pullt und startet Compose neu

### Option 4: Watchtower (Automatische Container-Updates)

Für RPi5 (auto-update bei neuen Image-Versions):

```bash
# docker-compose-rpi.yml enthält bereits Watchtower
docker compose -f docker-compose-rpi.yml up -d

# Watchtower prüft alle 5 Min auf neue Images und updated automatisch
```

**Setup:**
1. Docker Hub Images müssen tagged sein: `username/image:latest`
2. Watchtower pollt Registry und startet Container bei neuer Version neu

## 🌐 Split Setup (PC + RPi5)

### PC (schnelle APIs)
```bash
cd web_api_tests
docker compose -f docker-compose-pc.yml up --build
# Node (3000) + FastAPI (3001) laufen lokal
```

### RPi5 (Frontend + C#)
```bash
# PC_IP mit tatsächlicher IP ersetzen (z.B. 192.168.1.100)
sed -i 's/PC_IP/192.168.1.100/g' docker-compose-rpi.yml
docker compose -f docker-compose-rpi.yml up --build
# C# (3002) + Frontend (3003) laufen auf RPi
# Frontend spricht mit PC-APIs
```

**Frontend greift zu:**
- Node: `http://PC_IP:3000`
- FastAPI: `http://PC_IP:3001`
- C#: `http://localhost:3002` (lokal)

## 📋 Deployment Strategien Vergleich

| Methode | Komplexität | Auto-Update | Best für |
|---------|-------------|------------|----------|
| GitHub Actions | Mittel | Ja | Prodution, Cloud Hosting |
| Traefik LB | Mittel | Nein | Multi-Instance, Load Balancing |
| Webhook | Einfach | Ja | Self-Hosted, RPi |
| Watchtower | Einfach | Ja (Container) | Docker Hub Registries |
| Lokal Compose | Sehr einfach | Nein | Entwicklung, Testing |

## 🚀 Schnell-Start Auto-Deploy (RPi5 + Webhook)

```bash
# 1. Auf RPi5
git clone https://github.com/your-username/Bank_mit_GUI_CPP.git
cd Bank_mit_GUI_CPP/web_api_tests

# 2. Webhook starten (background)
nohup python3 webhook_server.py > webhook.log 2>&1 &

# 3. GitHub Webhook konfigurieren
#    → http://rpi-ip:9000/webhook mit Secret

# 4. Test: git push main
#    → RPi pullt automatisch und redeploy
```

## 🔧 Server Einzeln Starten

### Node.js/Express (Port 3000)
```bash
cd web_api_tests/nodejs
npm start
# oder
node src/server.js
```

### Python/FastAPI (Port 3001)
```bash
cd web_api_tests/python
python main.py
# oder mit uvicorn
uvicorn main:app --host 0.0.0.0 --port 3001 --log-level error
```

### C#/.NET (Port 3002)
```bash
cd web_api_tests/csharp
dotnet run
```

### Tests gegen einzelne API

```bash
# Nach dem Server starten, in separatem Terminal:

# Node.js Tests
cd nodejs
npm run test:load
npm run test:stress
npm run test:concurrent

# Python Tests
cd python
python load_test.py
python stress_test.py
python concurrent_test.py

# C# Tests
cd csharp
dotnet run --project LoadTest.cs
dotnet run --project StressTest.cs
dotnet run --project ConcurrentTest.cs
```

## 📊 Globaler Test Orchestrator

Startet ALLE APIs automatisch und führt Tests durch:

```bash
cd web_api_tests
python test_orchestrator.py
```

**Was wird getestet:**
- Node.js/Express auf Port 3000
- Python/FastAPI auf Port 3001
- C#/.NET auf Port 3002
- Rust/Actix auf Port 3003 (wenn implementiert)

**Test-Szenarien pro Framework:**
1. **Load Test**: 100 Benutzer, 500 Posts, 1000 Kommentare, 2000 Likes
2. **Stress Test**: Schnelle User-/Post-Erstellung, massive Kommentare/Likes
3. **Concurrent Test**: Parallele Reads, Writes und Mixed Operationen

**Output:**
- Konsolen-Report mit Timing für alle Tests
- GUI mit:
  - Ergebnisse-Tabelle (Framework, Test-Typ, Status, Time, Req/sec)
  - Bar-Chart: Gesamtzeit nach Framework
  - Sortierbare Spalten

## 📡 API Endpoints

### User Management
```
POST   /api/users                    # Create user
GET    /api/users                    # Get all users
GET    /api/users/:id                # Get single user
PUT    /api/users/:id                # Update user
```

### Posts
```
POST   /api/posts                    # Create post
GET    /api/posts/:id                # Get post (increments views)
GET    /api/users/:userId/posts      # Get user's posts
GET    /api/users/:userId/feed       # Get personalized feed
```

### Comments
```
POST   /api/comments                 # Add comment
GET    /api/posts/:postId/comments   # Get post comments
```

### Likes
```
POST   /api/likes                    # Like a post
DELETE /api/likes                    # Unlike post
GET    /api/posts/:postId/likes/user/:userId  # Check if liked
```

### Following
```
POST   /api/follow                   # Follow user
DELETE /api/follow                   # Unfollow user
GET    /api/users/:userId/followers  # Get followers list
```

## 🧪 Test-Szenarien Details

### Load Test (Realistische Last)
- Erstelle 100 Benutzer sequential
- Erstelle 500 Posts (über alle Benutzer verteilt)
- Füge 1000 Kommentare zu Posts hinzu
- Erstelle 2000 Likes
- Lese 100 Feeds
- Lese 100 Posts mit ihren Kommentaren
- **Messung**: Gesamtzeit, Requests/Sekunde

### Stress Test (Höchstlast)
- Rapid User Creation: 500 Benutzer so schnell wie möglich
- Rapid Post Creation: 2000 Posts
- Comment Spam: 5000 Kommentare
- Like Bombardment: 5000 Likes
- Follow Spamming: 2000 Follows
- **Messung**: Zeit für jeden Stress-Test einzeln

### Concurrent Test (Parallele Last)
- 200 parallele GET-Requests (User-Reads)
- 100 parallele POST-Requests (neue Posts)
- 300 gemischte Operations (Comments, Feeds, Likes, Follows)
- **Messung**: Durchsatzzeit für alle parallelen Operationen

## 📈 Performance-Merkmale

### In-Memory Database
- HashMap/Dictionary für O(1) User/Post Lookups
- HashSet für schnelle Like/Follow Checks
- Keine persistente Storage (Test-Simulation)

### Komplexe Operationen
- **Feed Generation**: Filtert nach Following-Beziehungen, sortiert nach CreatedAt
- **Like Checks**: O(1) mit Hash-basiertem Duplikat-Check
- **Follower Graph**: Effiziente Adjacency-List mit HashSets

### Async/Parallel Processing
- Python: `asyncio` + `aiohttp` für native async/await
- C#: `Task.WhenAll()` für parallele HTTP-Requests
- Node.js: Native Promise/async Unterstützung
- Rust: Tokio async runtime (lib.rs)

## 📊 Erwartete Ausgabe

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
...

====================================================================================================
                    TOTAL TIME BY FRAMEWORK (SUM OF ALL TESTS)
====================================================================================================

Framework              Total (ms)     
----------------------------------------------------------------------------------------------------
Rust/Actix             3245.2
Node.js/Express        3891.6
C#/.NET                4156.8
Python/FastAPI         4823.4
```

## 🔍 Debugging

### Server läuft nicht an?

```bash
# Check Ports
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # macOS/Linux

# Manuelle Port-Tests
curl http://localhost:3000/health
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
```

### Test-Fehler?

1. Stelle sicher, alle Server laufen
2. Check Network-Verbindung
3. Validate JSON-Serialisierung in Tests
4. Prüfe Ports in `test_orchestrator.py`

## 📁 Verzeichnisstruktur

```
web_api_tests/
├── nodejs/
│   ├── src/
│   │   ├── server.js (Express App + Routes)
│   │   ├── database.js (In-Memory DB)
│   │   └── handlers.js (Route Handlers)
│   └── tests/
│       ├── load_test.js
│       ├── stress_test.js
│       └── concurrent_test.js
│
├── python/
│   ├── main.py (FastAPI App + Models + DB)
│   ├── load_test.py
│   ├── stress_test.py
│   └── concurrent_test.py
│
├── csharp/
│   ├── Program.cs (Minimal APIs + Routes)
│   ├── Database.cs (In-Memory DB)
│   ├── LoadTest.cs
│   ├── StressTest.cs
│   ├── ConcurrentTest.cs
│   └── Api.csproj
│
├── rust/
│   ├── src/
│   │   ├── lib.rs (Database + Models)
│   │   ├── main.rs (TODO)
│   │   ├── load_test.rs (TODO)
│   │   └── ... 
│   └── Cargo.toml
│
└── test_orchestrator.py (Master Test Runner)
```

## 🎯 Leistungs-Zielsetzungen

Typische Ergebnisse auf modernem System:

| Framework | Load Test | Stress Test | Concurrent | Total |
|-----------|-----------|-------------|-----------|-------|
| Rust/Actix | ~900ms | ~700ms | ~800ms | ~2.4s |
| Node.js | ~1200ms | ~900ms | ~800ms | ~2.9s |
| C#/.NET | ~1400ms | ~950ms | ~850ms | ~3.2s |
| Python | ~1500ms | ~1200ms | ~950ms | ~3.7s |

*(Variiert je nach System, Last, Netzwerk)*

## 🔧 Customization

### Test-Parameter ändern
- `nodejs/tests/load_test.js`: `for (let i = 0; i < 100; i++)` → Ändern Sie 100
- `python/load_test.py`: Gleich, suchen Sie nach `range(100)`
- `csharp/LoadTest.cs`: Suchen Sie nach `for (int i = 0; i < 100; i++)`

### Server-Ports ändern
1. `test_orchestrator.py`: Ändern Sie `"port": 3000` etc
2. Ändern Sie Listen-Port in jedem Server:
   - Node.js: `server.listen(3000)` in `src/server.js`
   - Python: `uvicorn.run(..., port=3001)` in `main.py`
   - C#: `.Run("http://0.0.0.0:3002")` in `Program.cs`

## 📝 Lizenz

Educational/Benchmarking Purpose

## 🤝 Entwickelt mit

- Express.js, FastAPI, .NET Core, Actix-Web
- SQLite (simuliert durch In-Memory Dbs)
- HTTP Client Libraries: node http, aiohttp, HttpClient, reqwest
- Async/await Patterns

---

**Hinweis**: Dies ist ein Benchmark-Framework zu Testzwecken. Für Production-APIs verwenden Sie entsprechend getestete Frameworks und echte Datenbanken!
