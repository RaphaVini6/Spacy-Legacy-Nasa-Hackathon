# Demo

Educational website about the NASA probes and equipment that are still on the Moon, on Mars and in deep space:
what each one did, where it is, and how its parts could be reused by future missions.



## Structure

```
frontend/   React + Vite (port 5173)
backend/    ASP.NET Core 10 API (port 5000)
```

## Running

Needs .NET 10 SDK and Node 20+.

```bash
cp .env.example .env
dotnet run --project backend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173. API docs: http://localhost:5000/scalar

With Docker:

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:8090. API docs: http://localhost:5090/scalar

## API

| Method | Route | |
|---|---|---|
| GET | `/api/health` | status |
| GET | `/api/probes` | list (filters: `destination`, `status`, `type`, `search`) |
| GET | `/api/probes/{id}` | details |
| GET | `/api/missions` | missions |


## Data

- `backend/Data/probes.*.json` - artifacts from our research document (sources: NASA / NSSDCA)
- `frontend/public/images/probes/` - 3D renders made by the team and NASA public domain photos
