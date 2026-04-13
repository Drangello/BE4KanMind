# Kanban Backend API

A production-ready Kanban backend API built with Django and Django REST Framework. This repository contains purely the backend code (in the `BE/` directory), separated strictly from the frontend.

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Development and Testing

The backend is configured with comprehensive CORS support (`django-cors-headers`) to allow local frontend access natively (`CORS_ALLOW_ALL_ORIGINS = True`). tests are strictly required before merging any features. Run tests with:
```bash
python manage.py test
```

## API Endpoints

### Authentication Contract

Authentication uses DRF Token Authentication. Include `Authorization: Token <your_token>` in headers for protected endpoints. All failed login requests return `400 BAD REQUEST`.

#### Registration
`POST /api/registration/`
- **Payload:**
  ```json
  {
    "fullname": "John Doe",
    "email": "johndoe@example.com",
    "password": "StrongPassword123!",
    "repeated_password": "StrongPassword123!"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "token": "xxx",
    "fullname": "John Doe",
    "email": "johndoe@example.com",
    "user_id": 1
  }
  ```

#### Login
`POST /api/login/`
- **Payload:**
  ```json
  {
    "email": "johndoe@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "token": "xxx",
    "fullname": "John Doe",
    "email": "johndoe@example.com",
    "user_id": 1
  }
  ```
