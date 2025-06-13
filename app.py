from flask import Flask, render_template, g, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import psycopg2
import psycopg2.extras # For dictionary cursor
import os # For environment variables (recommended for credentials)
import threading
from azure.servicebus import ServiceBusClient, ServiceBusMessage

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

SERVICE_BUS_CONNECTION_STR = os.getenv("SERVICE_BUS_CONNECTION_STR")
SERVICE_BUS_QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME", "logingest")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")  # Should be set in production

app.secret_key = SECRET_KEY

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

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

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token)
    session['user'] = user
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def show_logs():
    if not g.db_conn:
        return render_template('logs.html', 
                               error_message="Failed to connect to the database. Please check server logs and configuration.", 
                               table_name=DB_TABLE, logs=[], columns=[],
                               user=session.get('user'))

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

    return render_template('logs.html', 
                           logs=logs_data, 
                           columns=column_names, 
                           table_name=DB_TABLE, 
                           error_message=error,
                           user=session.get('user'))

def process_service_bus_messages():
    if not SERVICE_BUS_CONNECTION_STR:
        print("No Azure Service Bus connection string provided.")
        return
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=SERVICE_BUS_CONNECTION_STR, logging_enable=True)
    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=SERVICE_BUS_QUEUE_NAME)
        with receiver:
            print("Listening for Service Bus messages...")
            for msg in receiver:
                try:
                    # Assume message body is a string or JSON string
                    body = str(msg)
                    print(f"Received message: {body}")
                    # Insert into DB (customize parsing as needed)
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute(
                                f"INSERT INTO {DB_TABLE} (log_level, message) VALUES (%s, %s)",
                                ("INFO", body)
                            )
                            conn.commit()
                    receiver.complete_message(msg)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    receiver.abandon_message(msg)

def start_service_bus_listener():
    t = threading.Thread(target=process_service_bus_messages, daemon=True)
    t.start()

# Start the Service Bus listener in the background when the app starts
start_service_bus_listener()

if __name__ == '__main__':
    # IMPORTANT: Set debug=False in a production environment!
    app.run(host='0.0.0.0', port=5000, debug=True)