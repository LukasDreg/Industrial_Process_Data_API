# Industrial Data API

Industrial Data API is a beginner-friendly, production-style FastAPI backend for storing, importing, and analyzing machine process measurements.

The project is designed as a GitHub portfolio backend. It demonstrates clean API design, SQLAlchemy ORM usage, PostgreSQL integration, Docker Compose setup, service-layer separation, input validation, error handling, CSV import, and automated endpoint tests without adding unnecessary complexity.

## Portfolio Summary

This backend simulates a small industrial monitoring service. A factory or workshop could use a service like this to store machine measurements such as temperature, RPM, and tool wear, then review basic statistics for process monitoring.

The project demonstrates:

- REST API development with FastAPI
- PostgreSQL persistence with SQLAlchemy ORM
- Pydantic request and response validation
- Clean separation between routes, services, schemas, models, and database configuration
- CSV ETL import for batch measurement data
- Basic analytics using SQL aggregate functions
- Docker Compose for local development
- Unit tests for core API endpoints

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Pydantic
- Pytest
- Docker
- Docker Compose

## Architecture

```text
                       +--------------------------+
                       |        API Client        |
                       |  Swagger / curl / tests  |
                       +------------+-------------+
                                    | HTTP
                                    v
+----------------------------------------------------------------+
|                         FastAPI App                            |
|                                                                |
|  +--------------+     +--------------+     +--------------+    |
|  | Measurements |     |     ETL      |     |   Analysis   |    |
|  |    Routes    |     |    Routes    |     |    Routes    |    |
|  +------+-------+     +------+-------+     +------+-------+    |
|         |                    |                    |            |
|         v                    v                    v            |
|  +----------------------------------------------------------+  |
|  |                    Service Layer                         |  |
|  |  MeasurementService | CsvEtlService | AnalysisService    |  |
|  +--------------------------+-------------------------------+  |
|                             |                                  |
|                             v                                  |
|  +----------------------------------------------------------+  |
|  |                 SQLAlchemy ORM Model                     |  |
|  |                      Measurement                         |  |
|  +--------------------------+-------------------------------+  |
+-----------------------------|----------------------------------+
                              |
                              v
                    +----------------------+
                    |      PostgreSQL      |
                    |  measurements table  |
                    +----------------------+
```

## Project Structure

```text
industrial-data-api/
├── app/
│   ├── main.py                     # FastAPI app, startup, exception handlers
│   ├── database/
│   │   ├── base.py                 # SQLAlchemy declarative base
│   │   └── session.py              # Database engine and session dependency
│   ├── models/
│   │   └── measurement.py          # SQLAlchemy Measurement model
│   ├── routes/
│   │   ├── measurements.py         # CRUD endpoints
│   │   ├── etl.py                  # CSV import endpoint
│   │   └── analysis.py             # Summary endpoint
│   ├── schemas/
│   │   └── measurement.py          # Pydantic validation and response schemas
│   └── services/
│       ├── measurement_service.py  # CRUD business logic
│       ├── etl_service.py          # CSV parsing/import logic
│       └── analysis_service.py     # SQL aggregate queries
├── tests/
│   └── test_measurements.py        # Endpoint tests using SQLite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Data Model

| Field | Type | Validation | Description |
| --- | --- | --- | --- |
| `id` | integer | Auto-generated | Primary key |
| `machine_id` | string | 1-100 characters, not blank | Machine identifier |
| `temperature` | float | -50 to 250 | Machine/process temperature |
| `rpm` | float | 0 to 50000 | Machine RPM |
| `tool_wear` | float | 0 to 100 | Tool wear percentage/value |
| `timestamp` | datetime | Optional ISO 8601 datetime | Measurement time |

If `timestamp` is omitted, the backend stores the current UTC time.

## Running with Docker Compose

```bash
git clone https://github.com/your-username/industrial-data-api.git
cd industrial-data-api
cp .env.example .env
docker compose up --build
```

Windows Command Prompt:

```cmd
copy .env.example .env
docker compose up --build
```

Services:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

Stop the project:

```bash
docker compose down
```

Remove the database volume too:

```bash
docker compose down -v
```

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/measurements` | Create a measurement |
| `GET` | `/measurements` | List measurements with pagination |
| `GET` | `/measurements/{id}` | Get one measurement by ID |
| `DELETE` | `/measurements/{id}` | Delete one measurement by ID |
| `POST` | `/etl/import-csv` | Import measurements from CSV |
| `GET` | `/analysis/summary` | Get min, max, and average values |

## Example API Requests and Responses

### Create a measurement

```bash
curl -X POST "http://localhost:8000/measurements" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "MACHINE-001",
    "temperature": 72.5,
    "rpm": 1450,
    "tool_wear": 12.7,
    "timestamp": "2026-06-02T09:30:00Z"
  }'
```

```json
{
  "machine_id": "MACHINE-001",
  "temperature": 72.5,
  "rpm": 1450,
  "tool_wear": 12.7,
  "timestamp": "2026-06-02T09:30:00Z",
  "id": 1
}
```

### List measurements

```bash
curl "http://localhost:8000/measurements?skip=0&limit=10"
```

```json
{
  "items": [
    {
      "machine_id": "MACHINE-001",
      "temperature": 72.5,
      "rpm": 1450,
      "tool_wear": 12.7,
      "timestamp": "2026-06-02T09:30:00Z",
      "id": 1
    }
  ],
  "total": 1
}
```

### Delete a measurement

```bash
curl -X DELETE "http://localhost:8000/measurements/1"
```

```text
204 No Content
```

### Import measurements from CSV

```csv
machine_id,temperature,rpm,tool_wear,timestamp
MACHINE-001,72.5,1450,12.7,2026-06-02T09:30:00Z
MACHINE-002,80.1,1320,18.4,2026-06-02T09:31:00Z
MACHINE-001,74.2,1500,13.1,
```

```bash
curl -X POST "http://localhost:8000/etl/import-csv" \
  -F "file=@measurements.csv"
```

```json
{
  "imported": 3,
  "failed": 0,
  "errors": []
}
```

### Get analysis summary

```bash
curl "http://localhost:8000/analysis/summary"
```

```json
{
  "temperature": {"min": 72.5, "max": 80.1, "average": 75.6},
  "rpm": {"min": 1320, "max": 1500, "average": 1423.33},
  "tool_wear": {"min": 12.7, "max": 18.4, "average": 14.07}
}
```

## Error Handling Examples

### Validation error

```json
{
  "error": "Validation error",
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "temperature"],
      "msg": "Input should be less than or equal to 250",
      "input": 999,
      "ctx": {"le": 250.0}
    }
  ]
}
```

### Not found error

```json
{
  "detail": "Measurement not found"
}
```

### CSV row error

```json
{
  "imported": 2,
  "failed": 1,
  "errors": [
    "Row 3: could not convert string to float: 'bad-value'"
  ]
}
```

## Running Tests

The tests use SQLite in memory, so PostgreSQL and Docker are not required for the test suite.

```bash
pip install -r requirements.txt
pytest
```

Current tests cover:

- Creating measurements
- Getting a measurement by ID
- Listing measurements
- Deleting measurements
- Rejecting invalid input
- Returning analysis summaries

## Design Choices

- Routes stay thin and handle HTTP details.
- Service classes contain CRUD, CSV import, and analysis logic.
- PostgreSQL is used for local development through Docker Compose.
- SQLite is used for tests to keep them fast and easy to run.
- Tables are created automatically at startup for a beginner-friendly setup.
- In a real production deployment, Alembic migrations should replace automatic table creation.

## Possible Improvements

This project intentionally stays small. Useful next steps would be:

- Add Alembic migrations
- Add filtering by `machine_id` and timestamp range
- Add authentication for write operations
- Add structured logging
- Add CI workflow for running tests on GitHub Actions

## License

This project is intended for learning and portfolio usage. Add your preferred license before publishing publicly.