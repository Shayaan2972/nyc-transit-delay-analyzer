from flask import Flask, render_template, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Enviornment variables
load_dotenv()

# Creating a flask app
app = Flask(__name__)

# Function to connect to the database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname = os.getenv("DB_dbname"),
            user = os.getenv("DB_user"),
            password = os.getenv("DB_password"),
            host = os.getenv("DB_host"),
            port = os.getenv("DB_port")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
# Home URL route
@app.route('/')
def home():
    return render_template('app.html')

# API route
@app.route('/api/delays')
def get_delays():
    conn = connect_to_database()

    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Query to get delays from the database
        cursor.execute("""
            Select train_line, alert_message, alert_type, created, updated 
            From subway_delays Order by updated desc
            Limit 50
        """)

        # Fetch the results
        rows = cursor.fetchall()

        # Convert into a dictionary
        delays = []
        for row in rows:
            delays.append({
                'train_line' : row[0],
                'alert_message' : row[1],
                'alert_type' : row[2],
                'created' : str(row[3]) if row[3] else None,
                'updated' : str(row[4]) if row[4] else None
            })
    
        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Returns delays in JSON format
        return jsonify(delays)

    except Exception as e:
        print(f"Error fetching from database: {e}")
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500
    
# Worst lines route
@app.route('/api/stats/worst-lines')
def worst_lines():
    conn = connect_to_database()

    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Query to get most delayed lines
        cursor.execute("""
            Select train_line, Count(*) as delay_count  
            From subway_delays
            Where created > NOW() - INTERVAL '7 days'
            Group by train_line
            Order by delay_count Desc
            Limit 50
        """)

        # Fetch the results
        rows = cursor.fetchall()

        # Convert into a dictionary
        stats = []
        for row in rows:
            stats.append({
                'train_line' : row[0],
                'delay_type' : row[1]
            })
    
        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Returns delays in JSON format
        return jsonify(stats)

    except Exception as e:
        print(f"Error fetching from database: {e}")
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500
    
# Delay types route
@app.route('/api/stats/delay-types')
def delay_types():
    conn = connect_to_database()

    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()

        # Query to get most delayed lines
        cursor.execute("""
            Select alert_type, Count(*) as delay_count  
            From subway_delays
            Where created > NOW() - INTERVAL '7 days'
            Group by alert_type
            Order by delay_count Desc
            Limit 50
        """)

        # Fetch the results
        rows = cursor.fetchall()

        # Convert into a dictionary
        types = []
        for row in rows:
            types.append({
                'alerts' : row[0],
                'count' : row[1]
            })
    
        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Returns delays in JSON format
        return jsonify(types)

    except Exception as e:
        print(f"Error fetching from database: {e}")
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
