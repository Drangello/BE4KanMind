# Kanban Board REST API

A Django REST Framework (DRF) backend for a collaborative Kanban Board application. It supports user authentication, board management, task tracking, and threaded comments.

## Setup & Run Locally

1. **Create and activate a virtual environment**:
   ```bash
python -m venv venv
   ```
   ```bash
# Windows:
venv\Scripts\activate
   ```
   ```bash
# macOS/Linux:
source venv/bin/activate
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
The API will be available at `http://127.0.0.1:8000/`.

---
## Testing

Run test suite:

```bash
python manage.py test
```

## Architecture & Apps

The monolith API is split into three main Django applications:

- **`auth_app`**: Identity management. Features custom User models logging in via Email. Returns Token Authentication keys.
- **`boards_app`**: Board management. Every Kanban board has a single owner and multiple invited members. 
- **`tasks_app`**: Tasks and comments. Tracks task status, priority, and assignees. Tasks strictly belong to a parent board.

## Security & Permissions

Security is strictly enforced on an object-level basis to prevent unauthorized data access (IDOR).
- **Authentication**: All major endpoints require an `Authorization: Token <key>` header.
- **Board Visibility**: Users can only fetch and update data for boards they own or are members of.
- **Role Actions**: 
  - Only **Owners** can delete their boards.
  - Only **Creators** or **Owners** can delete a task.
  - Only **Comment Authors** can delete their comments.

## Database Relationships

- **Cascading Deletes**: Deleting a Board removes all underlying Tasks. Deleting a Task removes all underlying Comments.
- **Data Preservation**: Deleting a user does NOT delete the tasks they reviewed or were assigned to; instead, their ID is set to `NULL` to preserve board history.