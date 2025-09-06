Mechanic Shop API
=================

Overview
--------
This project is a RESTful API for managing a mechanic shop. It allows users to sign up, log in, and manage mechanics, inventory parts, and service tickets. The API is built with Flask, SQLAlchemy, and JWT authentication. Swagger (Flasgger) is used for live API documentation, and unittest is used for automated testing.

Features
--------
- User management (signup, login, list, update, delete)
- JWT token authentication for protected routes
- Inventory management (list, get by id, create, update, delete)
- Mechanic management (list, get by id, create, update, delete)
- Service ticket management:
  * Create and list tickets
  * Assign and remove mechanics
  * Add inventory parts to a ticket
  * Delete tickets
- Swagger UI documentation for every route
- Automated unit tests with both positive and negative cases

Project Structure
-----------------
- main.py
  Entry point that creates the Flask app and registers all blueprints.

- config.py
  Contains environment configurations (Development, Testing, Production).
  The TestingConfig uses SQLite in-memory DB and disables rate limits.

- application/blueprints/users/routes.py
  User endpoints: signup, login, list users, get user by id, update, delete.
  All routes are documented with Swagger YAML docstrings.

- application/blueprints/inventory/routes.py
  Inventory endpoints: list parts, get part by id, create, update, delete.
  Create/Update/Delete are protected by JWT.

- application/blueprints/mechanics/routes.py
  Mechanic endpoints: list mechanics, get mechanic by id, create, update, delete.

- application/blueprints/tickets/routes.py
  Ticket endpoints: create, list, get by id, edit mechanics, add part, delete.

- tests/test_base.py
  Base test class (APITestCase) that sets up a fresh app and database for each test.
  Includes a helper (auth_headers) to sign up and log in a user and return JWT headers.

- tests/test_users.py
  Unit tests for user routes (signup, login, list, update, delete).

- tests/test_inventory.py
  Unit tests for inventory routes (list, create, get by id, update, delete).
  Includes positive and negative tests.

- tests/test_mechanics.py
  Unit tests for mechanic routes (list, create, get by id, update, delete).

- tests/test_tickets.py
  Unit tests for ticket routes (create, list, get by id, edit mechanics, add part, delete).

Setup Instructions
------------------
1. Clone the repository.
2. Create and activate a virtual environment:
   Windows PowerShell:
     python -m venv venv
     .\venv\Scripts\Activate.ps1
3. Install dependencies:
     pip install -r requirements.txt
4. Set environment variable for Flask:
     set FLASK_APP=main.py
5. Run the application:
     flask run

Swagger Documentation
---------------------
Once the app is running, open the Swagger UI in your browser:
   http://127.0.0.1:5000/apidocs/

All routes include tags, summary, parameters, security (for JWT-protected routes),
and example request/response payloads.

Testing
-------
1. Ensure you are in your virtual environment.
2. Run unit tests with:
     python -m unittest discover -s tests -p "test_*.py" -t .
3. 26 tests should run and all pass.
   Tests include both positive cases (successful requests) and negative cases
   (invalid input, unauthorized access, missing fields).

Notes
-----
- Some deprecation warnings may appear from SQLAlchemy (utcnow, Query.get);
  they do not affect functionality.
- Each test runs against a clean in-memory SQLite database.
- JWT tokens expire after 1 hour by default.

Author
------
Richard Kim
