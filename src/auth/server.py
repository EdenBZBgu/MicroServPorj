from time import timezone
from pytz import timezone
import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dotenv import load_dotenv

load_dotenv()
server = Flask(__name__)
mysql = MySQL(server)

# PASSPHRASE = os.getenv("PRIVATE_KEY_PASSPHRASE").encode()  # converts to bytes
PRIVATE_KEY_PATH = "private.pem"
PUBLIC_KEY_PATH = "public.pem"

server.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
server.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
server.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
server.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
server.config['MYSQL_PORT'] = os.environ.get('MYSQL_PORT')


def generate_keys():
    if os.path.exists(PRIVATE_KEY_PATH) and os.path.exists(PUBLIC_KEY_PATH):
        return

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(os.environ.get('PRIVATE_KEY_PASSPHRASE').encode())
        ))

    public_key = private_key.public_key()

    with open(PUBLIC_KEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


# --- Load keys ---
def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=os.environ.get('PRIVATE_KEY_PASSPHRASE').encode())


def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())


@server.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return {'message': 'Missing username / password'}, 401

    cursor = mysql.connection.cursor()
    res = cursor.execute("SELECT *, admin_priv FROM users WHERE username = %s", (auth.username,))

    if res > 0:
        user = cursor.fetchone()
        if auth.password != user['password'] or auth.username != user['username']:
            return {'message': 'Wrong username / password'}, 401

        return create_jwt(auth.username, auth.password, user['admin_priv'])

    return {'message': 'User not found'}, 401

def verify_token(token):
    try:
        payload = jwt.decode(token, load_public_key(), algorithms=['RS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

@server.route('/validate', methods=['POST'])
def validate():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return {'message': 'Wrong auth method'}, 401

    token = auth_header.split(" ")[1]

    try:
        payload = verify_token(token)
        return payload, 200
    except jwt.ExpiredSignatureError:
        return {'message': 'JW Token expired'}, 401
    except jwt.InvalidTokenError:
        return {'message': 'Invalid JWT'}, 401


def create_jwt(username, password, admin):
    payload = {
        'username': username,
        'password': password,
        'exp': datetime.datetime.now(tz=timezone('Asia/Jerusalem')) + datetime.timedelta(days=1),
        'iat': datetime.datetime.now(tz=timezone('Asia/Jerusalem')), # issued at
        'admin': bool(admin),
    }

    jwt_token = jwt.encode(payload, load_private_key(), algorithm='RS256')
    return jwt_token, 200

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=5000)
