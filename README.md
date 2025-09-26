# SecuredBank AI Service

A secure API service for banking AI operations with API key authentication.

## Features

- 🔐 API Key Authentication
- 🚀 FastAPI with async support
- 🛡️ CORS Protection
- 🧪 Test Suite
- 📝 OpenAPI Documentation
- ⚡ Rate Limiting

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for database operations)
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SecuredBank/ai-service.git
   cd ai-service
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env` and update the values as needed.

### Running the Application

Start the development server:
```bash
uvicorn src.server:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All endpoints except `/health` require an API key in the `X-API-Key` header.

Example:
```http
GET / HTTP/1.1
Host: localhost:8000
X-API-Key: default-secure-key-123
```

## Testing

Run the test suite:
```bash
pytest
```

## Configuration

Update the `.env` file to configure the application:

```env
# Application Settings
ENVIRONMENT=development
DEBUG=True

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Security
API_KEY_HEADER=X-API-Key
API_KEYS=["default-secure-key-123"]

# CORS (comma-separated list of origins, or empty for all)
BACKEND_CORS_ORIGINS=[]

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Rate Limiting
RATE_LIMIT=100/minute
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
