# Kanban Backend API (Django REST Framework)

A RESTful backend for a Kanban system built with Django REST Framework. It supports boards, tasks, and comments with strict role-based access control (owner/member) and secure object-level permissions.

The API is designed for clean architecture, predictable responses, and safe multi-user collaboration.

---

## Tech Stack

- Django 5.x
- Django REST Framework 3.x
- SQLite (development)
- Token Authentication

---

## Project Structure

BE/
├── core/
├── auth_app/
├── boards_app/
├── tasks_app/
├── manage.py

Each app follows a consistent structure:

api/
├── views.py
├── serializers.py
├── urls.py
├── permissions.py

---

## Installation

```bash
cd BE
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
Testing

Run full test suite:

python manage.py test

Run specific app tests:

python manage.py test tasks_app

Target coverage: 95%+

API Overview
Authentication
POST /api/registration/ – Create user
POST /api/login/ – Get auth token
Boards
GET /api/boards/ – List boards
POST /api/boards/ – Create board
GET /api/boards/{id}/ – Board details
PATCH /api/boards/{id}/ – Update members
DELETE /api/boards/{id}/ – Delete board (owner only)
Tasks
POST /api/tasks/ – Create task
PATCH /api/tasks/{id}/ – Update task
DELETE /api/tasks/{id}/ – Delete task
GET /api/tasks/assigned-to-me/ – My tasks
GET /api/tasks/reviewing/ – Review tasks
Comments
GET /api/tasks/{task_id}/comments/ – List comments
POST /api/tasks/{task_id}/comments/ – Add comment
DELETE /api/tasks/{task_id}/comments/{id}/ – Delete comment (author only)
Permissions
Boards
Owner: full control
Members: limited read/write access
Tasks
Accessible only to board members
Only creator or owner can delete
Comments
Only board members can create
Only author can delete

Unauthorized access:

401 unauthenticated
404 hidden resources (security by design)
Data Rules
Tasks belong to boards
Comments belong to tasks
Users only access boards they belong to
Board owner is assigned automatically
CORS

Configured for development:

CORS_ALLOW_ALL_ORIGINS = True

Restrict origins in production.

Project Goals
Clean REST architecture
Strict role-based access control
Predictable API behavior
Scalable frontend integration