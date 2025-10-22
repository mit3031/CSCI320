import psycopg
from sshtunnel import SSHTunnelForwarder

username = "RIT username"
password = "RIT password"
dbName = "db name"


try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'dbname': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port
        }


        conn = psycopg.connect(**params)
        curs = conn.cursor()
        print("Database connection established")

        #DB work here....

        conn.close()
except Exception as e:
    print(f"Connection failed {e}")