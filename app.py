from flask import Flask, render_template, g
import psycopg2
import psycopg2.extras # For dictionary cursor
import os # For environment variables (recommended for credentials)

app = Flask(__name__)

# --- Database Configuration ---
# It's highly recommended to use environment variables for sensitive data in production.
# For this example, we're using the provided values directly.
DB_HOST = os.getenv("DB_HOST", "mydbserver")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "myhost")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASS = os.getenv("DB_PASS", "mypass")
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")
DB_TABLE = "logs"

def get_db_connection():
    """Establishes a new database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            sslmode=DB_SSLMODE
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

@app.before_request
def before_request():
    """Get a database connection before each request."""
    g.db_conn = get_db_connection()

@app.teardown_request
def teardown_request(exception):
    """Close the database connection after each request."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

@app.route('/')
def show_logs():
    if not g.db_conn:
        return render_template('logs.html', 
                               error_message="Failed to connect to the database. Please check server logs and configuration.", 
                               table_name=DB_TABLE, logs=[], columns=[])

    logs_data = []
    column_names = []
    error = None

    try:
        # Using DictCursor to get rows as dictionaries (column_name: value)
        with g.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(f"SELECT * FROM {DB_TABLE};")
            if cur.description:
                column_names = [desc[0] for desc in cur.description]
            logs_data = cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        error = f"Error fetching data from table '{DB_TABLE}': {e}"
        # You might want to rollback if it was a write operation, g.db_conn.rollback()

    return render_template('logs.html', 
                           logs=logs_data, 
                           columns=column_names, 
                           table_name=DB_TABLE, 
                           error_message=error)

if __name__ == '__main__':
    # IMPORTANT: Set debug=False in a production environment!
    app.run(host='0.0.0.0', port=5000, debug=True)