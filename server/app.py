import os
import json
import re
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse
import sqlite3

import jwt
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client')), static_url_path='')
CORS(app)

# Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

# --- Environment Variables ---
DB_URL = os.getenv('DATABASE_URL', '')
JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET', '')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_SECURE = os.getenv('EMAIL_SECURE', 'false').lower() == 'true'
EMAIL_USER = os.getenv('EMAIL_USER', '')
EMAIL_PASS = os.getenv('EMAIL_PASS', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', EMAIL_USER)
EMAIL_API_ENABLED = os.getenv('EMAIL_API_ENABLED', 'false').lower() == 'true'
EMAIL_API_BASE = os.getenv('EMAIL_API_BASE', 'https://pro.api.serversmtp.com/api/v2').rstrip('/')
EMAIL_CONSUMER_KEY = os.getenv('EMAIL_CONSUMER_KEY', '')
EMAIL_CONSUMER_SECRET = os.getenv('EMAIL_CONSUMER_SECRET', '')
EMAIL_FALLBACK = os.getenv('EMAIL_FALLBACK', 'true').lower() != 'false'
VERIFICATION_EXPIRATION_MINUTES = int(os.getenv('VERIFICATION_EXPIRATION_MINUTES', 15))
OUTBOX_RETRY_BASE_SECONDS = int(os.getenv('OUTBOX_RETRY_BASE_SECONDS', 60))
ALLOW_DEV_CODE_IN_RESPONSE = os.getenv('ALLOW_DEV_CODE_IN_RESPONSE', '').lower() == 'true'
NODE_ENV = os.getenv('NODE_ENV', 'development')
PORT = int(os.getenv('PORT', 4000))

# Verification log file
VERIF_LOG = os.path.join(os.path.dirname(__file__), 'verification_debug.log')

# API Token cache
api_token_cache = {'token': None, 'expiresAt': 0}

# SMTP availability flag
SMTP_AVAILABLE = False

# Compatibility class for RealDictCursor with SQLite
class RealDictCursor:
    def __init__(self, connection):
        self.cursor = connection.cursor()

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

    def fetchall(self):
        columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def fetchone(self):
        columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
        row = self.cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

# --- Database Connection ---
def get_db_connection():
    """Get a database connection."""
    try:
        if DB_URL.startswith('sqlite:///'):
            db_path = DB_URL.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
            return conn
        else:
            # Fallback para otras bases de datos si es necesario
            raise ValueError("Unsupported database URL")
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# --- Email Setup ---
def verify_smtp():
    """Verify SMTP configuration."""
    global SMTP_AVAILABLE
    try:
        if not EMAIL_HOST or not EMAIL_USER:
            print('SMTP not configured (EMAIL_HOST or EMAIL_USER missing)')
            SMTP_AVAILABLE = False
            return
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=5) as server:
            if EMAIL_SECURE:
                server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
        SMTP_AVAILABLE = True
        print('SMTP transport ready. Emails will be sent via configured SMTP server.')
    except Exception as e:
        SMTP_AVAILABLE = False
        print(f'SMTP transport not available or misconfigured. Emails will not be sent. Error: {e}')

# Verify SMTP on startup
verify_smtp()

def send_email_smtp(to, subject, text):
    """Send email via SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text, 'plain'))
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10) as server:
            if EMAIL_SECURE:
                server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        return {'sent': True}
    except Exception as e:
        print(f'SMTP send failed: {e}')
        return {'sent': False, 'error': str(e)}

async def get_api_token():
    """Get API token from TurboSMTP or similar service."""
    if not EMAIL_API_ENABLED:
        return None
    
    if api_token_cache['token'] and datetime.now().timestamp() < api_token_cache['expiresAt'] - 30:
        return api_token_cache['token']
    
    try:
        response = requests.post(
            f"{EMAIL_API_BASE}/authorize",
            json={
                'consumerKey': EMAIL_CONSUMER_KEY.strip(),
                'consumerSecret': EMAIL_CONSUMER_SECRET.strip()
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f'Token request failed: {response.status_code} {response.text}')
            return None
        
        body = response.json()
        token = body.get('apiKey') or body.get('token')
        if not token and 'data' in body:
            token = body['data'].get('apiKey') or body['data'].get('token')
        
        expires_in = int(body.get('expiresIn') or body.get('expires_in') or 3600)
        
        if token:
            api_token_cache['token'] = token
            api_token_cache['expiresAt'] = datetime.now().timestamp() + expires_in
            print(f'Obtained API token for TurboSMTP (cached {expires_in}s)')
            return token
        
        print(f'No token found in authorize response: {body}')
        return None
    except Exception as e:
        print(f'Failed to fetch API token: {e}')
        return None

def send_email_api(to, subject, text):
    """Send email via API (TurboSMTP or similar)."""
    try:
        token = None
        try:
            token = get_api_token()
        except:
            pass
        
        if not token:
            return {'sent': False, 'error': 'No API token'}
        
        payload = {
            'mail': {
                'from': EMAIL_FROM,
                'to': [{'email': to}],
                'subject': subject,
                'text': text
            }
        }
        
        response = requests.post(
            f"{EMAIL_API_BASE}/mail/send",
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f'sendViaApi failed: {response.status_code} {response.text}')
            return {'sent': False, 'error': response.text}
        
        return {'sent': True, 'body': response.json()}
    except Exception as e:
        print(f'sendViaApi error: {e}')
        return {'sent': False, 'error': str(e)}

def enqueue_outbox(to_email, subject, text, payload=None):
    """Enqueue failed emails in the outbox table for retries."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        next_attempt = datetime.now() + timedelta(seconds=OUTBOX_RETRY_BASE_SECONDS)
        
        cur.execute(
            """INSERT INTO email_outbox (to_email, subject, text, payload, status, attempts, next_attempt_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (to_email, subject, text, json.dumps(payload or {}), 'pending', 0, next_attempt)
        )
        
        email_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        print(f'Email enqueued in outbox id {email_id} for {to_email}')
        return {'ok': True, 'id': email_id}
    except Exception as e:
        print(f'Error enqueueing email in outbox: {e}')
        return {'ok': False, 'error': str(e)}

def send_verification_email(to, code, subject, text):
    """Send verification email with fallback logic."""
    fallback_allowed = EMAIL_FALLBACK or NODE_ENV != 'production'
    
    if EMAIL_API_ENABLED:
        api_result = send_email_api(to, subject, text)
        if api_result['sent']:
            return {'sent': True, 'via': 'api'}
        print(f'API send did not succeed, falling back. Reason: {api_result.get("error", "unknown")}')
    
    if SMTP_AVAILABLE:
        smtp_result = send_email_smtp(to, subject, text)
        if smtp_result['sent']:
            return {'sent': True, 'via': 'smtp'}
        
        # If send failed, fall back to logging in development if allowed
        if fallback_allowed:
            entry = f"{datetime.now().isoformat()} | TO: {to} | CODE: {code} | SUBJ: {subject} | SEND_ERROR: {smtp_result.get('error')}\n"
            try:
                enqueue_outbox(to, subject, text, {'type': 'verification', 'code': code})
            except:
                pass
            
            try:
                with open(VERIF_LOG, 'a') as f:
                    f.write(entry)
                print(f'Email send failed; code logged to {VERIF_LOG} for {to}')
                return {'sent': False, 'fallback': True, 'logPath': VERIF_LOG}
            except Exception as e:
                print(f'Error writing verification debug log after send failure: {e}')
                return {'sent': False, 'error': str(e)}
        
        return {'sent': False, 'error': smtp_result.get('error', 'Unknown error')}
    
    # SMTP not available -> fallback to development logging if allowed
    if fallback_allowed:
        entry = f"{datetime.now().isoformat()} | TO: {to} | CODE: {code} | SUBJ: {subject}\n"
        try:
            enqueue_outbox(to, subject, text, {'type': 'verification', 'code': code})
        except:
            pass
        
        try:
            with open(VERIF_LOG, 'a') as f:
                f.write(entry)
            print(f'Email fallback: verification code logged to {VERIF_LOG} for {to}')
            return {'sent': False, 'fallback': True, 'logPath': VERIF_LOG}
        except Exception as e:
            print(f'Error writing verification debug log: {e}')
            return {'sent': False, 'error': str(e)}
    
    return {'sent': False, 'error': 'SMTP/API unavailable and fallback not allowed'}

# --- Utilities ---
def generate_code():
    """Generate a 7-digit verification code."""
    import random
    return str(random.randint(1000000, 9999999))

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hash_value):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))

def verify_jwt(token):
    """Verify and decode a JWT token."""
    try:
        if not JWT_SECRET:
            return None, 'SUPABASE_JWT_SECRET not configured'
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    except Exception as e:
        return None, str(e)

def require_bearer_token(f):
    """Decorator to require Bearer token in Authorization header."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token requerido'}), 401
        
        token = auth_header[7:]
        payload, error = verify_jwt(token)
        if error:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        return f(payload=payload, *args, **kwargs)
    return decorated_function

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print(f'Socket connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Socket disconnected: {request.sid}')

# --- API Routes ---

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint."""
    return jsonify({'ok': True})

@app.route('/api/auth/session', methods=['POST'])
@require_bearer_token
def auth_session(payload):
    """Create or sync user session from Supabase JWT."""
    email = payload.get('email')
    if not email or not email.lower().endswith('@tecmilenio.mx'):
        return jsonify({'error': 'Solo se permiten correos @tecmilenio.mx'}), 403
    
    try:
        metadata = payload.get('user_metadata', {})
        name = metadata.get('full_name') or metadata.get('name') or email.split('@')[0] or 'Usuario'
        user_type = metadata.get('user_type', 'employee')
        
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        # Check if user exists
        cur.execute(
            'SELECT id, email, name, user_type, image_url, description FROM users WHERE email = ?',
            (email,)
        )
        existing = cur.fetchone()
        
        if existing:
            # Update user to active
            cur.execute('UPDATE users SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (existing['id'],))
            conn.commit()
            
            conn.close()
            
            return jsonify({
                'ok': True,
                'user': {
                    'id': existing['id'],
                    'email': existing['email'],
                    'name': existing['name'],
                    'type': existing['user_type'],
                    'imageUrl': existing['image_url'],
                    'description': existing['description'] or ''
                }
            })
        
        # Create new user
        cur.execute(
            """INSERT INTO users (email, password_hash, name, user_type, image_url, description, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (email, '', name, user_type, None, None, 1)
        )
        user_id = cur.lastrowid
        
        # Create profile
        cur.execute(
            """INSERT INTO profiles (user_id, name, description, detailed_description, tech_stack, salary, image_url, role)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, '', '', json.dumps([]), '', None, 'job' if user_type == 'company' else 'candidate')
        )
        
        conn.commit()
        
        # Get profile and emit event
        try:
            cur.execute('SELECT * FROM profiles WHERE user_id = ? LIMIT 1', (user_id,))
            profile = cur.fetchone()
            socketio.emit('user_verified', {'user': {'id': user_id, 'email': email}, 'profile': dict(profile) if profile else None}, broadcast=True)
        except:
            pass
        
        
        conn.close()
        
        return jsonify({
            'ok': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'type': user_type,
                'imageUrl': None,
                'description': ''
            }
        })
    except Exception as e:
        print(f'Error in auth/session: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def auth_register():
    """Register a new user."""
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type', 'employee')
    
    if not name or not email or not password:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    if not email.lower().endswith('@tecmilenio.mx'):
        return jsonify({'error': 'El correo debe pertenecer al dominio @tecmilenio.mx'}), 400
    
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        # Check if user exists
        cur.execute('SELECT id, is_active FROM users WHERE email = ?', (email,))
        existing = cur.fetchone()
        
        if existing:
            if existing['is_active']:
                
                conn.close()
                return jsonify({'error': 'Correo ya registrado'}), 400
            
            # User exists but not active, resend code
            user_id = existing['id']
            code = generate_code()
            expires_at = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
            
            cur.execute(
                """INSERT INTO email_verifications (user_id, code, expires_at, verified)
                   VALUES (?, ?, ?, ?)""",
                (user_id, code, expires_at, 0)
            )
            conn.commit()
            
            subject = 'PlusZone - Código de verificación (reenvío)'
            text = f'Tu código de verificación de 7 dígitos es: {code}. El código expira en {VERIFICATION_EXPIRATION_MINUTES} minutos.'
            
            send_result = send_verification_email(email, code, subject, text)
            
            conn.close()
            
            if send_result['sent']:
                return jsonify({'ok': True, 'message': 'Cuenta existente pendiente de verificación. Se ha reenviado un código.'})
            
            if send_result.get('fallback'):
                response = {'ok': True, 'warning': 'No se pudo enviar el correo. Código guardado en el servidor (verification_debug.log).'}
                if ALLOW_DEV_CODE_IN_RESPONSE:
                    response['devCode'] = code
                return jsonify(response)
            
            return jsonify({'error': 'No se pudo enviar el correo de verificación. Contacta al administrador.'}), 500
        
        # Create new user
        password_hash = hash_password(password)
        cur.execute(
            """INSERT INTO users (email, password_hash, name, user_type, image_url, description, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (email, password_hash, name, user_type, None, None, 0)
        )
        user_id = cur.lastrowid
        
        # Create profile
        cur.execute(
            """INSERT INTO profiles (user_id, name, description, detailed_description, tech_stack, salary, image_url, role)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, name, '', '', json.dumps([]), '', None, 'job' if user_type == 'company' else 'candidate')
        )
        
        # Generate verification code
        code = generate_code()
        expires_at = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
        cur.execute(
            """INSERT INTO email_verifications (user_id, code, expires_at, verified)
               VALUES (?, ?, ?, ?)""",
            (user_id, code, expires_at, 0)
        )
        
        conn.commit()
        
        subject = 'PlusZone - Código de verificación'
        text = f'Tu código de verificación de 7 dígitos es: {code}. El código expira en {VERIFICATION_EXPIRATION_MINUTES} minutos.'
        
        send_result = send_verification_email(email, code, subject, text)
        
        conn.close()
        
        if send_result['sent']:
            return jsonify({'ok': True, 'message': 'Usuario registrado. Revisa tu correo para verificar la cuenta.'})
        
        if send_result.get('fallback'):
            response = {'ok': True, 'warning': 'Cuenta creada, pero no se pudo enviar el correo. Revisa la consola del servidor o el archivo verification_debug.log en la carpeta server.'}
            if ALLOW_DEV_CODE_IN_RESPONSE:
                response['devCode'] = code
            return jsonify(response)
        
        response = {'ok': True, 'warning': 'Cuenta creada, pero no se pudo enviar el correo de verificación. Usa Reenviar código en el modal o configura el email.'}
        if ALLOW_DEV_CODE_IN_RESPONSE:
            response['devCode'] = code
        return jsonify(response)
    except Exception as e:
        print(f'Error in auth/register: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/auth/verify', methods=['POST'])
@limiter.limit("10 per minute")
def auth_verify():
    """Verify email with code."""
    data = request.get_json() or {}
    email = data.get('email')
    code = data.get('code')
    
    if not email or not code:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        # Get user
        cur.execute('SELECT id, is_active FROM users WHERE email = ?', (email,))
        user = cur.fetchone()
        if not user:
            
            conn.close()
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Get verification record
        cur.execute(
            """SELECT id, code, expires_at, verified FROM email_verifications
               WHERE user_id = ? ORDER BY id DESC LIMIT 1""",
            (user['id'],)
        )
        record = cur.fetchone()
        if not record:
            
            conn.close()
            return jsonify({'error': 'Código no encontrado. Solicita uno nuevo.'}), 404
        
        if record['verified']:
            
            conn.close()
            return jsonify({'error': 'Código ya verificado'}), 400
        
        if datetime.now() > record['expires_at']:
            
            conn.close()
            return jsonify({'error': 'Código expirado'}), 400
        
        if record['code'] != code:
            
            conn.close()
            return jsonify({'error': 'Código incorrecto'}), 400
        
        # Mark as verified
        cur.execute('UPDATE email_verifications SET verified = 1 WHERE id = ?', (record['id'],))
        cur.execute('UPDATE users SET is_active = 1 WHERE id = ?', (user['id'],))
        conn.commit()
        
        # Emit socket event
        try:
            cur.execute('SELECT * FROM profiles WHERE user_id = ? LIMIT 1', (user['id'],))
            profile = cur.fetchone()
            socketio.emit('user_verified', {'user': {'id': user['id'], 'email': email}, 'profile': dict(profile) if profile else None}, broadcast=True)
        except:
            pass
        
        
        conn.close()
        
        return jsonify({'ok': True, 'message': 'Correo verificado correctamente'})
    except Exception as e:
        print(f'Error in auth/verify: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/auth/resend', methods=['POST'])
@limiter.limit("5 per minute")
def auth_resend():
    """Resend verification code."""
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requerido'}), 400
    
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        # Get user
        cur.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cur.fetchone()
        if not user:
            
            conn.close()
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Check rate limit
        cur.execute(
            """SELECT COUNT(*) as cnt FROM email_verifications
               WHERE user_id = ? AND created_at > datetime('now', '-1 hour')""",
            (user['id'],)
        )
        cnt = cur.fetchone()['cnt']
        if cnt >= 3:
            
            conn.close()
            return jsonify({'error': 'Has solicitado demasiados códigos. Intenta más tarde.'}), 429
        
        # Generate new code
        code = generate_code()
        expires_at = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
        cur.execute(
            """INSERT INTO email_verifications (user_id, code, expires_at, verified)
               VALUES (?, ?, ?, ?)""",
            (user['id'], code, expires_at, 0)
        )
        conn.commit()
        
        subject = 'PlusZone - Código de verificación (reenvío)'
        text = f'Tu código de verificación de 7 dígitos es: {code}. El código expira en {VERIFICATION_EXPIRATION_MINUTES} minutos.'
        
        send_result = send_verification_email(email, code, subject, text)
        
        conn.close()
        
        if send_result['sent']:
            return jsonify({'ok': True, 'message': 'Código reenviado. Revisa tu correo.'})
        
        if send_result.get('fallback'):
            response = {'ok': True, 'warning': 'No se pudo enviar el correo. Revisa verification_debug.log en la carpeta server.'}
            if ALLOW_DEV_CODE_IN_RESPONSE:
                response['devCode'] = code
            return jsonify(response)
        
        return jsonify({'error': 'Error interno'}), 500
    except Exception as e:
        print(f'Error in auth/resend: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def auth_login():
    """Login with email and password."""
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        cur.execute(
            """SELECT id, email, password_hash, name, user_type, image_url, description, is_active
               FROM users WHERE email = ?""",
            (email,)
        )
        user = cur.fetchone()
        
        conn.close()
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Correo no verificado. Revisa tu bandeja y verifica tu cuenta con el código de 7 dígitos.'}), 403
        
        return jsonify({
            'ok': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'type': user['user_type'],
                'imageUrl': user['image_url'],
                'description': user['description'] or ''
            }
        })
    except Exception as e:
        print(f'Error in auth/login: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles of active users."""
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        cur.execute(
            """SELECT p.*, u.email, u.user_type, u.is_active
               FROM profiles p
               JOIN users u ON p.user_id = u.id
               WHERE u.is_active = 1
               ORDER BY p.created_at DESC"""
        )
        profiles = cur.fetchall()
        conn.close()
        
        return jsonify({'ok': True, 'profiles': [dict(p) for p in profiles]})
    except Exception as e:
        print(f'Error in get_profiles: {e}')
        return jsonify({'error': 'Error interno'}), 500
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create a new profile for an existing user."""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    name = data.get('name')
    role = data.get('role', 'candidate')
    
    if not user_id or not name:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        conn = get_db_connection()
        cur = RealDictCursor(conn)
        
        cur.execute(
            """INSERT INTO profiles (user_id, name, role) VALUES (?, ?, ?)""",
            (user_id, name, role)
        )
        new_id = cur.lastrowid
        
        conn.commit()
        
        # Get the new profile and emit event
        try:
            cur.execute(
                """SELECT p.*, u.email, u.user_type FROM profiles p
                   JOIN users u ON p.user_id = u.id WHERE p.id = ? LIMIT 1""",
                (new_id,)
            )
            new_profile = cur.fetchone()
            if new_profile:
                socketio.emit('profile_created', {'profile': dict(new_profile)}, broadcast=True)
        except:
            pass
        
        
        conn.close()
        
        return jsonify({'ok': True, 'id': new_id})
    except Exception as e:
        print(f'Error in create_profile: {e}')
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/analyze-cv', methods=['POST'])
def analyze_cv():
    """Analyze CV content and extract skills (internally, no separate service)."""
    data = request.get_json() or {}
    text = data.get('text', '').lower()
    
    skills = []
    
    if 'javascript' in text or 'js' in text:
        skills.append('JavaScript')
    if 'python' in text:
        skills.append('Python')
    if 'react' in text:
        skills.append('React')
    if 'vue' in text or 'vuejs' in text:
        skills.append('Vue')
    if 'angular' in text:
        skills.append('Angular')
    if 'node' in text or 'nodejs' in text:
        skills.append('Node.js')
    if 'java' in text and 'javascript' not in text:
        skills.append('Java')
    if 'c#' in text or 'csharp' in text or 'c sharp' in text:
        skills.append('C#')
    if 'php' in text:
        skills.append('PHP')
    if 'sql' in text or 'postgresql' in text or 'mysql' in text:
        skills.append('SQL')
    if 'docker' in text:
        skills.append('Docker')
    if 'kubernetes' in text or 'k8s' in text:
        skills.append('Kubernetes')
    if 'aws' in text:
        skills.append('AWS')
    if 'git' in text:
        skills.append('Git')
    if 'devops' in text:
        skills.append('DevOps')
    if 'machine learning' in text or 'ml' in text or 'ai' in text:
        skills.append('Machine Learning')
    
    return jsonify({
        'skills': list(set(skills)),  # Remove duplicates
        'score': len(set(skills)) * 20
    })

# --- Serve Static Files ---
@app.route('/', methods=['GET'])
def serve_index():
    """Serve index.html for SPA."""
    client_path = os.path.join(os.path.dirname(__file__), '..', 'client', 'index.html')
    if os.path.exists(client_path):
        return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'client'), 'index.html')
    return jsonify({'error': 'index.html not found'}), 404

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files from client directory."""
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    client_path = os.path.join(os.path.dirname(__file__), '..', 'client')
    file_path = os.path.join(client_path, path)
    
    # Security: prevent directory traversal
    if not os.path.abspath(file_path).startswith(os.path.abspath(client_path)):
        return jsonify({'error': 'Not found'}), 404
    
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            return send_from_directory(client_path, os.path.join(path, 'index.html'))
        return send_from_directory(client_path, path)
    
    # SPA fallback
    return send_from_directory(client_path, 'index.html')

# --- Database Setup ---
def ensure_database_ready():
    """Ensure database tables exist; create them if necessary."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Try to query users table to check if it exists
        try:
            cur.execute('SELECT 1 FROM users LIMIT 1')
            print('Database ready: tables available.')
            
            conn.close()
            return
        except Exception as e:
            if 'no such table' in str(e).lower() or 'table' not in str(e).lower():
                print('Tables missing detected. Running migrations...')

                # Run migrations for SQLite - execute each statement separately
                migration_statements = [
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255),
                        name VARCHAR(255),
                        user_type VARCHAR(50) DEFAULT 'employee',
                        image_url TEXT,
                        description TEXT,
                        is_active INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS email_verifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        code VARCHAR(10) NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        verified INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name VARCHAR(255),
                        description TEXT,
                        detailed_description TEXT,
                        tech_stack TEXT DEFAULT '[]',
                        salary VARCHAR(100),
                        image_url TEXT,
                        role VARCHAR(50) DEFAULT 'candidate',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS email_outbox (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        to_email VARCHAR(255) NOT NULL,
                        subject VARCHAR(255),
                        text TEXT,
                        payload TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        attempts INTEGER DEFAULT 0,
                        last_error TEXT,
                        next_attempt_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """,
                    "CREATE INDEX IF NOT EXISTS idx_email_outbox_status_next ON email_outbox(status, next_attempt_at);",
                    "CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_email_verifications_user_id ON email_verifications(user_id);"
                ]
                
                for statement in migration_statements:
                    cur.execute(statement)
                
                conn.commit()
                print('Migrations executed successfully.')
            
            conn.close()
    except Exception as e:
        print(f'Error ensuring database: {e}')
        raise

# --- Ensure .env exists ---
def ensure_env_file():
    """Ensure .env file exists, copy from .env.example if present."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    example_path = os.path.join(os.path.dirname(__file__), '.env.example')
    
    if not os.path.exists(env_path) and os.path.exists(example_path):
        import shutil
        shutil.copy(example_path, env_path)
        print('Archivo `.env` no encontrado. Se ha creado a partir de `.env.example`. Revisa `server/.env` y completa las credenciales si es necesario.')

# --- Startup ---
if __name__ == '__main__':
    ensure_env_file()
    
    try:
        ensure_database_ready()
    except Exception as e:
        print(f'Error preparing database: {e}')
        import sys
        sys.exit(1)
    
    print(f'API + Socket.IO server listening on port {PORT}')
    socketio.run(app, host='0.0.0.0', port=PORT, debug=NODE_ENV == 'development')
