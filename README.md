# 🔗 URL Shortener & Analytics API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.14+-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-Production-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![roadmap](https://roadmap.sh/projects/url-shortening-service)
**A scalable, production-ready URL Shortener API — with custom aliases, expiration, JWT auth, Redis caching, and deep click analytics.**

[Features](#-features) • [Architecture](#️-architecture) • [Getting Started](#-getting-started) • [API Reference](#-api-reference) • [Caching](#-caching-strategy) • [Roadmap](#-roadmap)

</div>

---

## 📌 Overview

A fully-featured URL shortening service built with **Django REST Framework**, designed with clean backend architecture in mind. Every component has a single responsibility — Views delegate to Services, Services delegate to Selectors, and the Caching layer sits transparently between them.

The project runs in **Docker** with **Gunicorn** as the WSGI server, **PostgreSQL** for persistence, and **Redis** for high-speed caching — ready for production out of the box.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔗 **URL Shortening** | Generate short codes for any long URL |
| ✏️ **Custom Alias** | Define your own short code (e.g. `/go`, `/sale`) |
| ⏳ **Expiration Dates** | Set a TTL — links auto-expire when the time is up |
| 📊 **Deep Analytics** | Track total clicks, unique IPs, referrers, and timestamps |
| ⚡ **Redis Caching** | Cache-Aside pattern with automatic invalidation |
| 📄 **Pagination** | Efficiently browse large URL datasets |
| 🔐 **JWT Auth** | Secure, stateless authentication via Bearer tokens |
| 🏗️ **Clean Architecture** | Services + Selectors pattern for maximum maintainability |
| 🐳 **Fully Dockerized** | One command to run the entire stack |

---

## 🏗️ Architecture

The project enforces strict separation of concerns. Business logic never lives in views.

```
project/
│
├── config/
│   ├── responses.py          # Standardized API response format
│   └── exceptions.py         # Global exception handlers
│
└── shortener/
    ├── models.py              # URL & Click data models
    ├── serializers.py         # Request/Response serialization
    ├── views.py               # Thin views — delegate to services
    │
    ├── selectors/             # Read-only DB query logic
    │   ├── url_selectors.py
    │   └── analytics_selectors.py
    │
    ├── services/              # Write & business logic
    │   ├── url_services.py
    │   └── cache_service.py
    │
    └── analytics/             # Click tracking & aggregation
```

**Why this structure?**
- **Views** — only handle HTTP input/output, no logic
- **Services** — all write operations and business rules
- **Selectors** — all read queries, reusable across the codebase
- **Cache Service** — centralized Redis logic, easy to swap or extend

---

## ⚙️ Tech Stack

```
Backend         →  Django + Django REST Framework
Auth            →  JWT (SimpleJWT)
Database        →  PostgreSQL
Caching         →  Redis (Cache-Aside pattern)
Server          →  Gunicorn (production WSGI)
Containerization→  Docker + Docker Compose
```

---

## 🐳 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/HossamHassan999/url-shortener.git
cd url-shortener
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Django
DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production

# PostgreSQL
POSTGRES_DB=shortener
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

> ⚠️ **Never commit `.env` to version control.** Use `.env.example` as a reference template.

### 3. Build & Run

```bash
docker compose up --build
```

This starts three containers: `web` (Django + Gunicorn), `db` (PostgreSQL), and `redis`.

### 4. The API is live at

```
http://localhost:8000
```

---

## 📡 API Reference

All responses follow a unified envelope format:

```json
{
  "success": true,
  "message": "Human-readable message",
  "data": {}
}
```

### Authentication

All protected endpoints require a JWT Bearer token:

```
Authorization: Bearer <access_token>
```

---

### Endpoints

#### 🔗 Create Short URL
```
POST /api/urls/
```

```json
// Request
{
  "original_url": "https://example.com/very/long/path",
  "custom_alias": "go"
}

// Response 201
{
  "success": true,
  "message": "Short URL created",
  "data": {
    "short_code": "go"
  }
}
```

---

#### 📄 List URLs (Paginated)
```
GET /api/urls/?page=1
```

```json
// Response 200
{
  "success": true,
  "message": "URLs retrieved successfully",
  "data": {
    "count": 20,
    "next": "http://localhost:8000/api/urls/?page=2",
    "previous": null,
    "results": []
  }
}
```

Default page size: **5 URLs per page**

---

#### 🔀 Redirect
```
GET /api/urls/redirect/{short_code}
```

Resolves the short code and returns a `302` redirect to the original URL. The click is recorded atomically inside a database transaction.

---

#### 📊 URL Analytics
```
GET /api/urls/{id}/analytics/
```

```json
// Response 200
{
  "success": true,
  "message": "Detailed analytics retrieved",
  "data": {
    "total_clicks": 120,
    "unique_ips": 30,
    "top_referrers": ["https://twitter.com", "https://google.com"],
    "recent_clicks": []
  }
}
```

---

#### 📈 Click Events
```
GET /api/clicks/?url_id=<id>
```

Returns all click events for a URL. Each event captures:

| Field | Description |
|---|---|
| `ip_address` | Visitor's IP |
| `user_agent` | Browser / device info |
| `referrer` | Traffic source |
| `timestamp` | When the click occurred |

---

## ⚡ Caching Strategy

The API uses the **Cache-Aside pattern** via Redis for high-throughput reads.

### Cache Keys & TTL

| Resource | Cache Key | TTL |
|---|---|---|
| URL list page | `user:{user_id}:urls:page:{page}` | 60 seconds |
| URL analytics | `url_analytics:{url_id}` | 300 seconds |

### How It Works

```
Read Request
    ↓
Check Redis → HIT  → Return cached data instantly
    ↓
           → MISS → Query PostgreSQL → Store in Redis → Return data

Write / Delete → Invalidate matching cache keys automatically
```

---

## 🔐 Security

- **JWT Authentication** — stateless, no server-side session storage
- **Object-level permissions** — users can only manage their own URLs
- **No sequential IDs exposed** — use UUID or opaque identifiers in responses
- **Environment-based config** — no secrets in source code

> For production: set `DEBUG=False`, use a strong `SECRET_KEY`, and configure `ALLOWED_HOSTS`.

---

## 🧪 Roadmap

Planned improvements for future versions:

- [ ] Rate limiting per user / IP
- [ ] QR code generation for each short URL
- [ ] Link preview metadata (Open Graph)
- [ ] Background jobs with **Celery + Celery Beat**
- [ ] Geo-location analytics (country, city)
- [ ] Custom domain support
- [ ] Admin dashboard with charts

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.


