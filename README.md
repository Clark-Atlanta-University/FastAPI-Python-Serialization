# FastAPI-Python-Serialization
## Project Description
This project implements FastAPI using Command Line Arguments defined by the client. It supports CRUD operations, nested object validation with Pydantic, JSON serialization, and HTTP Basic Authentication. 

The Python client uses argparse subparsers and the requests library to communicate with the server.

## Setup Instructions
1. Create and clone a new GitHub repository
  git glone <repo_link>
2. Create and activate a virtual environment
  python -m venv .venv
  ./.venv/Scripts/activate
3. Install dependencies
  pip install -r requirements.txt
4. Run the Server
  cd server
  python main.py (Use CTRL + C to shutdown)
5. Run the Python Client (Using command line arguments)
  cd client
  python client.py <argument1> <argument2> --<optional_argument1> <optional_argument1>

## Exercises Implemented
Exercise #1) Search Books by Genre (Server and Client)
Exercise #3) Partial Update with PATCH (Server and Client)
Exercise #4) Basic Authentication (Server)
Exercise #5) Book Count Endpoint (Server and Client)
