# app.py

from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# ================= POSTGRESQL =================
conn = psycopg2.connect("postgresql://users:SftiBTFxZZCFdvzwegWO97d1KmRoSDqX@dpg-d8ogk94vikkc73f4r2g0-a/backend-db")

cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# ================= CREATE TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    number VARCHAR(15) NOT NULL,
    address TEXT,
    pincode VARCHAR(10),
    aadhar_no VARCHAR(12),
    password VARCHAR(100) NOT NULL
)
""")

conn.commit()


# ===================================================
# REGISTER API
# ===================================================
@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    number = data.get("number")
    address = data.get("address")
    pincode = data.get("pincode")
    aadhar_no = data.get("aadhar_no")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if password != confirm_password:
        return jsonify({
            "status": False,
            "message": "Passwords do not match"
        }), 400

    try:
        sql = """
        INSERT INTO users
        (name, email, number, address, pincode, aadhar_no, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (name, email, number, address, pincode, aadhar_no, password))
        conn.commit()

        return jsonify({
            "status": True,
            "message": "User registered successfully"
        }), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({
            "status": False,
            "message": "Email already exists"
        }), 400

    except Exception as e:
        conn.rollback()
        return jsonify({
            "status": False,
            "message": str(e)
        }), 500


# ===================================================
# LOGIN API
# ===================================================
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    sql = """
    SELECT id, name, email, number, address, pincode, aadhar_no
    FROM users
    WHERE email = %s AND password = %s
    """

    cursor.execute(sql, (email, password))
    user = cursor.fetchone()

    if user:
        return jsonify({
            "status": True,
            "message": "Login successful",
            "user": dict(user)
        }), 200

    return jsonify({
        "status": False,
        "message": "Invalid email or password"
    }), 401


# ===================================================
# GET ALL USERS
# ===================================================
@app.route('/users', methods=['GET'])
def get_users():

    cursor.execute("""
        SELECT id, name, email, number, address, pincode, aadhar_no
        FROM users
    """)

    rows = cursor.fetchall()

    return jsonify([dict(row) for row in rows])


# ===================================================
# UPDATE USER
# ===================================================
@app.route('/update/<int:id>', methods=['PUT'])
def update_user(id):

    data = request.get_json()

    name = data.get("name")
    number = data.get("number")
    address = data.get("address")
    pincode = data.get("pincode")
    aadhar_no = data.get("aadhar_no")

    sql = """
    UPDATE users
    SET name = %s, number = %s, address = %s, pincode = %s, aadhar_no = %s
    WHERE id = %s
    """

    cursor.execute(sql, (name, number, address, pincode, aadhar_no, id))
    conn.commit()

    return jsonify({
        "status": True,
        "message": "User updated successfully"
    })


# ===================================================
# DELETE USER
# ===================================================
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):

    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()

    return jsonify({
        "status": True,
        "message": "User deleted successfully"
    })


# ===================================================
# FORGOT PASSWORD
# ===================================================
@app.route('/forgot_password', methods=['PUT'])
def forgot_password():

    data = request.get_json()

    email = data.get("email")
    number = data.get("number")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if new_password != confirm_password:
        return jsonify({
            "status": False,
            "message": "Passwords do not match"
        }), 400

    cursor.execute(
        "SELECT id FROM users WHERE email = %s AND number = %s",
        (email, number)
    )

    user = cursor.fetchone()

    if not user:
        return jsonify({
            "status": False,
            "message": "Email or mobile number is incorrect"
        }), 404

    cursor.execute(
        "UPDATE users SET password = %s WHERE email = %s AND number = %s",
        (new_password, email, number)
    )

    conn.commit()

    return jsonify({
        "status": True,
        "message": "Password updated successfully"
    }), 200


# ===================================================
# START SERVER
# ===================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )