# 🗺️ PortMap

![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![nginx](https://img.shields.io/badge/nginx-alpine-009639?logo=nginx&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

> **A self-hosted web dashboard for scanning open/closed ports across multiple hosts — all in one Docker Compose.**

Набридло постійно гадати, який порт вільний? PortMap — локальна веб-панель, яка сканує порти на будь-яких IP-адресах у вашій мережі та показує наочну карту: що відкрито, що закрито, і який сервіс за цим стоїть.

---

## ✨ Features

- 🔍 **Scan any host** — localhost, LAN IPs, or any reachable hostname
- ⚡ **Parallel scanning** — 200 concurrent threads, full range in seconds
- 🗂️ **60+ known services** — SSH, HTTP, MySQL, Redis, Docker, Kafka, RabbitMQ, Kubernetes…
- 🎯 **Flexible ranges** — common ports / custom range (1–65535) / comma-separated list
- 💾 **Persistent host list** — saved between sessions via localStorage
- 🌓 **Dark terminal UI** — built with vanilla JS, zero dependencies on the frontend
- 🐳 **One command deploy** — `docker compose up -d --build`

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/portmap.git
cd portmap
docker compose up -d --build
```

Open **http://localhost:8787** in your browser.

> **Requirements:** Docker + Docker Compose (v2). Nothing else.

---

## 🖥️ Usage

1. **Add a host** — type an IP or hostname in the sidebar and press `+`
2. **Choose scan mode:**
   - `Common` — ~60 most popular ports (fast, good default)
   - `Range` — e.g. `1` to `65535`
   - `Custom` — e.g. `80, 443, 3000, 8080`
3. **Pick a timeout** — fast (0.3s) / standard (0.5s) / slow (1.5s for distant hosts)
4. **Click Scan** — results appear as a filterable port grid

Filter by **Open / Closed**, search by port number or service name.

---

## 🏗️ Architecture

```
Browser :8787
    └── nginx (frontend container)
            └── static HTML + vanilla JS

Browser → API calls → :5000
    └── Flask + Gunicorn (backend container, network_mode: host)
            └── Python socket scanner (200 threads)
```

The backend runs with `network_mode: host` so it can reach real machine ports — not just the isolated Docker network.

| Container | Image | Port |
|---|---|---|
| `portmap-ui` | nginx:alpine | 8787 |
| `portmap-api` | python:3.12-slim | 5000 |

---

## 📁 Project Structure

```
portmap/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py          # Flask API + port scanner
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── index.html      # Single-file UI (HTML + CSS + JS)
```

---

## ⚙️ Configuration

No config files needed. Everything works out of the box.

**Change the UI port** (default `8787`) in `docker-compose.yml`:
```yaml
ports:
  - "9000:80"   # change 9000 to whatever you want
```

**Change the API port** (default `5000`):
```yaml
ports:
  - "5001:5000"
```
And update the `API` variable in `frontend/index.html` accordingly.

---

## 🛠️ Development

**Backend only** (no Docker):
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Rebuild after changes:**
```bash
docker compose up -d --build
```

**View logs:**
```bash
docker compose logs -f
```

---

## 📡 API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scan` | Scan ports on a host |
| `POST` | `/api/ping` | Check if host is reachable |
| `GET` | `/api/local` | Get local hostname & IP |
| `GET` | `/health` | Health check |

**Scan request body:**
```json
{
  "host": "192.168.1.1",
  "range": "common",
  "timeout": 0.5
}
```
`range` can be `"common"`, `"range"` (+ `start`/`end`), or `"custom"` (+ `ports: [80, 443]`).

---

## 🤝 Contributing

PRs are welcome. Ideas for improvement:

- [ ] Export results to CSV / JSON
- [ ] Auto-rescan on schedule
- [ ] UDP port scanning
- [ ] Notifications on port state changes
- [ ] Multi-host parallel scanning

---

## 📄 License

MIT — do whatever you want with it.
