# Task Manager REST API (Flask)

A simple **REST API** for managing personal tasks with **JWT authentication**.

## Features
- User registration & login (JWT)
- CRUD for tasks (Create, Read, Update, Delete)
- SQLite database (easy local run)

## Tech Stack
- Python
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- SQLite

## API Endpoints

### Auth
- `POST /auth/register`  
  Body: `{ "email": "user@mail.com", "password": "secret123" }`

- `POST /auth/login`  
  Body: `{ "email": "user@mail.com", "password": "secret123" }`  
  Response: `{ "access_token": "..." }`

### Tasks (requires Authorization header)
Header:
`Authorization: Bearer <access_token>`

- `GET /tasks`
- `POST /tasks`  
  Body: `{ "title": "Buy milk", "description": "2 bottles" }`
- `GET /tasks/<id>`
- `PUT /tasks/<id>`  
  Body example: `{ "title": "Buy milk", "is_done": true }`
- `DELETE /tasks/<id>`

## Run Locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
