Allowance Management Backend

A backend system for managing personal allowance, tracking spending, calculating available budgets, and suggesting suitable places based on the available budget.

Features

* Select an allowance period:
    * Daily
    * Weekly
    * Monthly
    * Yearly
    * Custom
* Automatically calculate the number of days for the selected allowance period.
* Support leap years for yearly allowances.
* Calculate the daily spending budget.
* Record spending.
* Calculate the remaining balance.
* Calculate the remaining days.
* Calculate the remaining daily budget.
* Add places with expected costs.
* Store and retrieve places using PostgreSQL.
* Suggest suitable places based on the available budget.
* Validate user inputs and return clear error messages.
* Document and interactively test the REST API using Swagger.

Technologies

* Python
* Flask
* Object-Oriented Programming (OOP)
* PostgreSQL
* psycopg2
* REST API
* Swagger / OpenAPI
* Flasgger
* Postman

Project Structure

Allowance Implementation/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── Project Planning.txt
├── Pseudocode.txt
├── Testing.txt
│
├── database/
│   └── connection.py
│
├── models/
│   ├── allowance.py
│   ├── spending.py
│   └── place.py
│
└── diagrams/
    ├── Use Case Diagram.png
    ├── Activity Diagram.png
    └── Class Diagram.png

System Architecture

Client / Postman / Swagger
          ↓
      Flask REST API
          ↓
 Python Business Logic
          ↓
      PostgreSQL

The system uses Flask to provide REST API endpoints, Python classes to handle the main business logic, and PostgreSQL for persistent data storage.

API Endpoints

Method	Endpoint	Description
GET	/	Check API status
POST	/allowance	Create a new allowance
POST	/spending	Record spending
POST	/places	Add a new place
GET	/places	Retrieve all saved places
GET	/suggestions?budget=10	Get suitable places based on the available budget

Allowance Periods

The system supports five allowance periods:

* Daily: 1 day
* Weekly: 7 days
* Monthly: Number of days in the selected month
* Yearly: 365 or 366 days depending on the year
* Custom: User-defined number of days

Examples

Daily:
10 JOD / 1 day = 10 JOD daily budget
Weekly:
70 JOD / 7 days = 10 JOD daily budget
Custom:
100 JOD / 10 days = 10 JOD daily budget

For monthly allowances, the system uses the selected month and year to determine the correct number of days.

For yearly allowances, the system checks whether the selected year is a leap year.

Creating an Allowance

The /allowance endpoint creates a new allowance.

Example request:

{
    "amount": 200,
    "period": "Daily"
}

Example response:

{
    "message": "Allowance created successfully.",
    "allowance_id": 1,
    "amount": 200.0,
    "period": "Daily",
    "number_days": 1,
    "daily_budget": 200.0,
    "remaining_balance": 200.0
}

Spending

The /spending endpoint records spending against an existing allowance.

Example request:

{
    "allowance_id": 1,
    "amount": 2
}

The system validates the spending amount and updates the allowance information.

The following values are updated or calculated:

* Remaining balance
* Remaining days
* Remaining daily budget

Remaining Daily Budget Formula

Remaining Daily Budget = Remaining Balance / Remaining Days

Example:

Remaining Balance = 198 JOD
Remaining Days = 29
198 / 29 = 6.83 JOD

Places

The system allows the user to save places together with their expected spending.

Example request:

{
    "name": "McDonald's",
    "expected_cost": 5
}

Example response:

{
    "message": "Place added successfully.",
    "place_id": 1,
    "name": "McDonald's",
    "expected_cost": 5.0
}

Retrieving Places

The /places endpoint retrieves all saved places.

Example:

GET /places

The system returns the saved places and their expected costs.

Suggestions

The /suggestions endpoint returns places that fit within the available budget.

Example:

GET /suggestions?budget=10

The system compares each place’s expected cost with the available budget.

Expected Cost <= Available Budget

Only places that satisfy this condition are returned.

If no suitable places are found, the system returns an empty suggestions list with a message.

Example:

{
    "message": "No suitable places were found.",
    "suggestions": []
}

Database

The project uses PostgreSQL for persistent data storage.

Allowances Table

allowances
-------------------------
allowance_id     PK
amount
period
number_days
daily_budget
remaining_balance
start_date
created_at

Spendings Table

spendings
-------------------------
spending_id      PK
allowance_id     FK
amount
created_at

Places Table

places
-------------------------
place_id         PK
name
expected_cost

Database Relationship

allowances
     │
     │ 1
     │
     │
     │ 0..*
     ▼
spendings
places
(independent)

Each allowance can have multiple spending records.

The allowance_id in the spendings table references the allowance_id in the allowances table.

Object-Oriented Design

The project uses Object-Oriented Programming with three main classes:

Allowance

Responsible for allowance-related calculations:

* Calculate daily budget
* Update remaining balance
* Calculate remaining daily budget

Spending

Responsible for spending validation.

Place

Responsible for place information and place validation.

Development Process

The project follows the Iterative Model.

The system is developed in multiple iterations, with each iteration being implemented and tested before moving to the next one.

Iteration 1 - Allowance and Spending

The first iteration focuses on the core functionality:

* Select allowance period
* Validate allowance amount
* Calculate number of days
* Calculate daily spending budget
* Record spending
* Validate spending
* Calculate remaining balance
* Calculate remaining days
* Calculate remaining daily budget

Iteration 2 - Place Management

The second iteration adds:

* Add places
* Validate place information
* Store places in PostgreSQL
* Retrieve saved places

Iteration 3 - Place Suggestions

The third iteration adds:

* Receive available budget
* Compare expected place costs with the available budget
* Return suitable places

API Documentation

Swagger / OpenAPI is used to document and interactively test the REST API.

The project uses Flasgger to integrate Swagger documentation with the Flask application.

After starting the application, open:

http://127.0.0.1:5000/apidocs/

Swagger provides documentation for the available endpoints, including:

* HTTP methods
* Request parameters
* Request body structure
* Example inputs
* Response status codes
* Response descriptions

The documented endpoints can also be tested directly through Swagger UI.

Testing

The system was tested using Postman to verify the REST API endpoints, input validation, business logic, and database persistence.

The following areas were tested:

* Daily allowance
* Weekly allowance
* Monthly allowance
* Yearly allowance
* Custom allowance
* Allowance amount validation
* Custom number of days validation
* Monthly and yearly date calculations
* Leap year calculation
* Valid spending
* Spending exceeding remaining balance
* Negative spending
* Remaining balance calculation
* Remaining days calculation
* Remaining daily budget calculation
* Valid place creation
* Negative place cost validation
* Retrieving saved places
* Suitable place suggestions
* No suitable place suggestions
* PostgreSQL data storage and retrieval
* Invalid inputs
* Swagger API documentation

All performed test cases passed successfully.

Requirements

The project dependencies are listed in requirements.txt.

Flask
psycopg2-binary
flasgger

Installation

1. Clone the repository

git clone <repository-url>

2. Open the project folder

cd "Allowance Implementation"

3. Install the required packages

pip install -r requirements.txt

4. Configure PostgreSQL

Create the PostgreSQL database:

allowance_db

Configure the database connection in:

database/connection.py

5. Run the application

python main.py

The Flask API will run locally.

API Access

Main API:

http://127.0.0.1:5000/

Swagger UI:

http://127.0.0.1:5000/apidocs/

Examples:

GET  http://127.0.0.1:5000/
GET  http://127.0.0.1:5000/places
GET  http://127.0.0.1:5000/suggestions?budget=10

POST endpoints:

POST http://127.0.0.1:5000/allowance
POST http://127.0.0.1:5000/spending
POST http://127.0.0.1:5000/places

Error Handling

The system validates user inputs and returns appropriate HTTP status codes.

Examples include:

* Missing request body
* Missing required fields
* Invalid allowance amount
* Invalid allowance period
* Invalid number of days
* Invalid month or year
* Negative spending
* Spending exceeding the remaining balance
* Invalid place cost
* Invalid budget
* Allowance not found
* Database errors

Documentation

The project includes:

* Project Planning
* Functional Requirements
* Non-Functional Requirements
* Constraints
* Pseudocode
* Use Case Diagram
* Activity Diagram
* Class Diagram
* Testing Documentation
* API Documentation using Swagger

Future Improvements

Possible future improvements include:

* User authentication
* Support for multiple users
* User-specific allowances and places
* Frontend integration
* Additional recommendation features
* Improved budget management
* Cloud deployment