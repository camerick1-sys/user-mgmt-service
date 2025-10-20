# User Management API (Flask + PostgreSQL + Docker)

This service provides user CRUD endpoints, JWT auth for protected routes, pagination, and Swagger docs.

## Quick Start
```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8000/health
```

### Example Requests
```bash
# Create (public)
curl -X POST http://localhost:8000/api/v1/users   -H "Content-Type: application/json"   -d '{"email":"test@example.com","password":"supersecret","full_name":"Test User"}'

# Login (JWT)
curl -X POST http://localhost:8000/auth/login   -H "Content-Type: application/json"   -d '{"email":"test@example.com","password":"supersecret"}'

# List (public, paginated)
curl "http://localhost:8000/api/v1/users?limit=10&offset=0"

# Update (protected)
curl -X PATCH http://localhost:8000/api/v1/users/1   -H "Authorization: Bearer <TOKEN>"   -H "Content-Type: application/json"   -d '{"full_name":"New Name"}'
```

## API Docs (Swagger)
Open: `http://localhost:8000/apidocs`

## Testing
```bash
pip install -r requirements.txt
pytest -q
```

## Endpoints
- `GET /health`
- `POST /api/v1/users`
- `GET /api/v1/users?limit=&offset=`
- `GET /api/v1/users/<id>`
- `PATCH /api/v1/users/<id>` (JWT)
- `DELETE /api/v1/users/<id>` (JWT)
- `POST /auth/login`
## Design Decisions
- Flask + SQLAlchemy; gunicorn in container.
- JWT (HS256) short-lived tokens.
- Passwords hashed with bcrypt.
- Pydantic validation; consistent error codes (400/401/404/409).
- Pagination on /api/v1/users (limit clamped 1..100).
- Docker Compose orchestrates pi + db, named volume for persistence; service DNS db.
- Swagger UI for manual QA at /apidocs.

## Submission Checklist
- [x] Dockerfile
- [x] docker-compose.yml (API + PostgreSQL + healthcheck)
- [x] DB schema auto-creates on first run
- [x] CRUD endpoints + validation + hashing
- [x] JWT auth (login + protected update/delete)
- [x] Pagination on list users
- [x] Tests (pytest)
- [x] CI (GitHub Actions)
- [x] README with setup/run
