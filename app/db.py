import psycopg
from sshtunnel import SSHTunnelForwarder
from flask import current_app, g
import atexit

server = None

def get_db():
    global server

    if 'db' not in g:
        if server is None or not server.is_active:
            raise RuntimeError("SSH tunnel not active")
    
    try:
        params = {
            'dbname': current_app.config['DB_NAME'],
            'user': current_app.config['RIT_USERNAME'],
            'password': current_app.config['RIT_PASSWORD'],
            'host': 'localhost',
            'port': server.local_bind_port
        }

        g.db = psycopg.connect(**params)
        print("DB connection established for request")
    except psycopg.Error as e:
        print(f"DB connection failed for this request: {e}")
        raise e
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
        print("DB connection closed for this request")

def init_db(app):
    global server

    if server is None:
        try:
            user = app.config["RIT_USERNAME"]
            pasw = app.config["RIT_PASSWORD"]

            print("Attempting to SSH tunnel")
            server = SSHTunnelForwarder(
                ('starbug.cs.rit.edu', 22),
                ssh_username=user,
                ssh_password=pasw,
                remote_bind_address=('127.0.0.1', 5432)
            )

            server.start()
            print(f"SSH tunnel established on local port {server.local_bind_port}")

            atexit.register(server.stop)
        except Exception as e:
            raise RuntimeError(f"Failed to start SSH tunnel: {e}")
    
    app.teardown_appcontext(close_db)
