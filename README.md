<h1 align="center">Kanban Board REST API</h1>

<p align="center">A Django REST Framework (DRF) backend for a collaborative Kanban Board application. It supports user authentication, board management, task tracking, and threaded comments.</p>

## Setup & Run Locally

Follow these steps to get your development environment set up:

### 1. Create and activate a virtual environment
```bash
python -m venv venv
```
**Windows:**
```bash
venv\Scripts\activate
```
**macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment variables

Create a .env file based on .env.example:
```bash
cp .env.example .env
```

### 4. Run database migrations
```bash
python manage.py migrate
```

### 5. Start the development server
```bash
python manage.py runserver
```
> The API will be available at `http://127.0.0.1:8000/`.

## Architecture & Apps

The monolith API is split into three decoupled Django applications to maintain clean architecture:

| App | Description |
|---|---|
| **`auth_app`** | Identity management. Features custom User models logging in via Email. Returns Token Authentication keys. |
| **`boards_app`** | Board management. Every Kanban board has a single owner and multiple invited members. |
| **`tasks_app`** | Tasks and comments tracking. Tracks task status, priority, and assignees. Tasks strictly belong to a parent board. |

---

## Security & Permissions

Security is strictly enforced on an object-level basis:

- **Authentication:** All major endpoints require an `Authorization: Token <key>` header.
- **Board Visibility:** Users can only fetch and update data for boards they own or are explicitly invited to as members.
- **Role Actions:** 
  - Only **Owners** can delete their boards.
  - Only **Creators** or **Owners** can delete a task.
  - Only **Comment Authors** can delete their own comments.

---

## Database Relationships

- **Cascading Deletes:** Deleting a *Board* guarantees the removal of all underlying *Tasks*. Deleting a *Task* removes all underlying *Comments*.
- **Data Preservation:** Deleting a user account does **NOT** delete the tasks they reviewed or were assigned to. Instead, their User ID is safely set to `NULL` to preserve board history and prevent data loss.