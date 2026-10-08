from flask import Flask, request, jsonify
from flasgger import Swagger
import psycopg2
import calendar
from datetime import date

from database.connection import create_connection
from models.allowance import Allowance
from models.spending import Spending
from models.place import Place


app = Flask(__name__)
swagger = Swagger(app)


# Calculate the number of days for the selected allowance period.
def get_number_of_days(period, number_days=None, month=None, year=None):

    if period == "Daily":
        return 1

    elif period == "Weekly":
        return 7

    elif period == "Monthly":
        if month is None or year is None:
            raise ValueError("Month and year are required for Monthly period.")

        month = int(month)
        year = int(year)

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        if year <= 0:
            raise ValueError("Year must be greater than 0.")

        return calendar.monthrange(year, month)[1]

    elif period == "Yearly":
        if year is None:
            raise ValueError("Year is required for Yearly period.")

        year = int(year)

        if year <= 0:
            raise ValueError("Year must be greater than 0.")

        return 366 if calendar.isleap(year) else 365

    elif period == "Custom":
        if number_days is None:
            raise ValueError("Number of days is required for Custom period.")

        number_days = int(number_days)

        if number_days <= 0:
            raise ValueError("Number of days must be greater than 0.")

        return number_days

    else:
        raise ValueError("Invalid allowance period.")


# Save the allowance in the database.
def save_allowance(allowance):

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO allowances
        (amount, period, number_days, daily_budget,
         remaining_balance, start_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
        RETURNING allowance_id
        """,
        (
            allowance.amount,
            allowance.period,
            allowance.number_days,
            allowance.daily_budget,
            allowance.remaining_balance
        )
    )

    allowance_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return allowance_id


# Check if the API is running.
@app.route("/", methods=["GET"])
def home():

    """
    Check API status.

    ---
    tags:
      - General
    produces:
      - application/json
    responses:
      200:
        description: API is running.
    """

    return jsonify({
        "message": "Allowance API is running."
    })


# Create a new allowance.
@app.route("/allowance", methods=["POST"])
def create_allowance():

    """
    Create a new allowance.

    ---
    tags:
      - Allowance
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - period
          properties:
            amount:
              type: number
              example: 200
            period:
              type: string
              example: Daily
            number_days:
              type: integer
              example: 10
            month:
              type: integer
              example: 2
            year:
              type: integer
              example: 2026
    responses:
      201:
        description: Allowance created successfully.
      400:
        description: Invalid input.
      500:
        description: Database error.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required."
            }), 400

        amount = data.get("amount")
        period = data.get("period")

        if amount is None or period is None:
            return jsonify({
                "error": "Amount and period are required."
            }), 400

        amount = float(amount)

        if amount <= 0:
            return jsonify({
                "error": "Allowance amount must be greater than 0."
            }), 400

        period = str(period).capitalize()

        number_days = get_number_of_days(
            period,
            data.get("number_days"),
            data.get("month"),
            data.get("year")
        )

        allowance = Allowance(
            amount,
            period,
            number_days
        )

        allowance.calculate_daily_budget()

        allowance_id = save_allowance(allowance)

        return jsonify({
            "message": "Allowance created successfully.",
            "allowance_id": allowance_id,
            "amount": allowance.amount,
            "period": allowance.period,
            "number_days": allowance.number_days,
            "daily_budget": round(allowance.daily_budget, 2),
            "remaining_balance": allowance.remaining_balance
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except psycopg2.Error as error:
        return jsonify({
            "error": "Database error.",
            "details": str(error)
        }), 500


# Record spending and update the remaining allowance.
@app.route("/spending", methods=["POST"])
def record_spending():

    """
    Record a new spending.

    ---
    tags:
      - Spending
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - allowance_id
            - amount
          properties:
            allowance_id:
              type: integer
              example: 1
            amount:
              type: number
              example: 2
    responses:
      200:
        description: Spending recorded successfully.
      400:
        description: Invalid input.
      404:
        description: Allowance not found.
      500:
        description: Database error.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required."
            }), 400

        allowance_id = data.get("allowance_id")
        amount = data.get("amount")

        if allowance_id is None or amount is None:
            return jsonify({
                "error": "Allowance ID and spending amount are required."
            }), 400

        allowance_id = int(allowance_id)
        amount = float(amount)

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT number_days, remaining_balance, start_date
            FROM allowances
            WHERE allowance_id = %s
            """,
            (allowance_id,)
        )

        allowance = cursor.fetchone()

        if not allowance:
            cursor.close()
            connection.close()

            return jsonify({
                "error": "Allowance not found."
            }), 404

        number_days, remaining_balance, start_date = allowance

        spending = Spending(amount)

        if amount < 0:
            cursor.close()
            connection.close()

            return jsonify({
                "error": "Spending amount cannot be negative."
            }), 400

        if not spending.validate_amount(remaining_balance):
            cursor.close()
            connection.close()

            return jsonify({
                "error": "Spending exceeds remaining balance."
            }), 400

        new_remaining_balance = remaining_balance - amount

        elapsed_days = (date.today() - start_date).days
        remaining_days = number_days - elapsed_days

        if remaining_days > 0:
            remaining_daily_budget = (
                new_remaining_balance / remaining_days
            )
        else:
            remaining_days = 0
            remaining_daily_budget = new_remaining_balance

        cursor.execute(
            """
            INSERT INTO spendings
            (allowance_id, amount)
            VALUES (%s, %s)
            """,
            (allowance_id, amount)
        )

        cursor.execute(
            """
            UPDATE allowances
            SET remaining_balance = %s
            WHERE allowance_id = %s
            """,
            (new_remaining_balance, allowance_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "message": "Spending recorded successfully.",
            "allowance_id": allowance_id,
            "spending_amount": amount,
            "remaining_balance": round(new_remaining_balance, 2),
            "remaining_days": remaining_days,
            "remaining_daily_budget": round(
                remaining_daily_budget, 2
            )
        }), 200

    except ValueError:
        return jsonify({
            "error": "Invalid input."
        }), 400

    except psycopg2.Error as error:
        return jsonify({
            "error": "Database error.",
            "details": str(error)
        }), 500


# Add a new place with its expected cost.
@app.route("/places", methods=["POST"])
def add_place():

    """
    Add a new place.

    ---
    tags:
      - Places
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - expected_cost
          properties:
            name:
              type: string
              example: McDonald's
            expected_cost:
              type: number
              example: 5
    responses:
      201:
        description: Place added successfully.
      400:
        description: Invalid input.
      500:
        description: Database error.
    """

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body is required."
            }), 400

        name = data.get("name")
        expected_cost = data.get("expected_cost")

        if not name or expected_cost is None:
            return jsonify({
                "error": "Place name and expected cost are required."
            }), 400

        expected_cost = float(expected_cost)

        place = Place(name, expected_cost)

        if not place.validate_place():
            return jsonify({
                "error": "Expected cost cannot be negative."
            }), 400

        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO places (name, expected_cost)
            VALUES (%s, %s)
            RETURNING place_id
            """,
            (place.name, place.expected_cost)
        )

        place_id = cursor.fetchone()[0]

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "message": "Place added successfully.",
            "place_id": place_id,
            "name": place.name,
            "expected_cost": place.expected_cost
        }), 201

    except ValueError:
        return jsonify({
            "error": "Expected cost must be a number."
        }), 400

    except psycopg2.Error as error:
        return jsonify({
            "error": "Database error.",
            "details": str(error)
        }), 500


# Retrieve all saved places.
@app.route("/places", methods=["GET"])
def get_places():

    """
    Get all saved places.

    ---
    tags:
      - Places
    produces:
      - application/json
    responses:
      200:
        description: List of saved places.
      500:
        description: Database error.
    """

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT place_id, name, expected_cost
            FROM places
            ORDER BY place_id
            """
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        places = []

        for row in rows:
            places.append({
                "place_id": row[0],
                "name": row[1],
                "expected_cost": float(row[2])
            })

        return jsonify(places), 200

    except psycopg2.Error as error:
        return jsonify({
            "error": "Database error.",
            "details": str(error)
        }), 500


# Find places that fit within the available budget.
@app.route("/suggestions", methods=["GET"])
def get_suggestions():

    """
    Get suitable places based on available budget.

    ---
    tags:
      - Suggestions
    produces:
      - application/json
    parameters:
      - in: query
        name: budget
        required: true
        type: number
        example: 10
    responses:
      200:
        description: Suitable places found or no suitable places available.
      400:
        description: Invalid budget.
      500:
        description: Database error.
    """

    budget = request.args.get("budget")

    if budget is None:
        return jsonify({
            "error": "Budget is required."
        }), 400

    try:
        budget = float(budget)

    except ValueError:
        return jsonify({
            "error": "Budget must be a number."
        }), 400

    if budget < 0:
        return jsonify({
            "error": "Budget cannot be negative."
        }), 400

    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name, expected_cost
            FROM places
            WHERE expected_cost <= %s
            ORDER BY expected_cost
            """,
            (budget,)
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        if not rows:
            return jsonify({
                "message": "No suitable places were found.",
                "suggestions": []
            }), 200

        suggestions = []

        for row in rows:
            suggestions.append({
                "name": row[0],
                "expected_cost": float(row[1])
            })

        return jsonify({
            "suggestions": suggestions
        }), 200

    except psycopg2.Error as error:
        return jsonify({
            "error": "Database error.",
            "details": str(error)
        }), 500


# Start the Flask API.
if __name__ == "__main__":
    app.run(debug=True)