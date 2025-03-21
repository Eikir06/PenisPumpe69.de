from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import shutil
import datetime

app = Flask(__name__)

# ** Secret Key für Sessions & Flash Messages **
app.secret_key = 'supersecretkey'

# ** SQLite-Datenbank einbinden **
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ** Upload-Konfiguration **
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
CONVERTED_FOLDER = os.path.join(BASE_DIR, 'converted')
IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
VIDEO_FORMATS = {'mp4', 'avi', 'mkv', 'mov', 'webm'}
AUDIO_FORMATS = {'mp3', 'wav', 'ogg', 'aac'}
DOCUMENT_FORMATS = {'pdf', 'docx', 'txt', 'html', 'epub', 'odt', 'pages'}

ALLOWED_EXTENSIONS = IMAGE_FORMATS | VIDEO_FORMATS | AUDIO_FORMATS | DOCUMENT_FORMATS


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

# Erstelle benötigte Ordner
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# ** Datenbank-Modelle definieren **
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prename = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Passwort wird jetzt gehasht gespeichert!

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default="random")
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

# ** Datenbank erstellen, falls nicht vorhanden **
with app.app_context():
    db.create_all()

# ** Benutzer-Datenbank (Test-Benutzer) **
user_data = {
    "Test12": {"password": generate_password_hash("12345"), "role": "Administrator"},
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_conversion(input_ext, target_ext):
    """Prüft, ob eine Konvertierung innerhalb derselben Dateigruppe möglich ist"""
    if input_ext in IMAGE_FORMATS and target_ext in IMAGE_FORMATS:
        return True
    if input_ext in VIDEO_FORMATS and target_ext in VIDEO_FORMATS:
        return True
    if input_ext in AUDIO_FORMATS and target_ext in AUDIO_FORMATS:
        return True
    if input_ext in DOCUMENT_FORMATS and target_ext in DOCUMENT_FORMATS:
        return True
    return False

def convert_file(filepath, target_format):
    """Simuliert eine Konvertierung durch Umbenennen der Datei"""
    filename, ext = os.path.splitext(os.path.basename(filepath))
    input_format = ext.lstrip('.').lower()

    if not is_valid_conversion(input_format, target_format):
        return None  # Ungültige Konvertierung

    new_filename = f"{filename}_converted.{target_format}"
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], new_filename)

    # Simulierte Konvertierung: Datei kopieren und umbenennen
    shutil.copy(filepath, converted_path)
    
    return new_filename  # Gibt den neuen Dateinamen zurück

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Prüfe zuerst, ob der Benutzer in der Datenbank existiert
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = user.username
            session['role'] = "Administrator" if user.username == "Test12" else "Nutzer"
            flash('Erfolgreich eingeloggt!', 'success')
            return redirect(url_for('homepage'))
        
        # Falls der Benutzer nicht in der DB ist, prüfe das Test-Dictionary
        elif username in user_data and check_password_hash(user_data[username]["password"], password):
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user_data[username]["role"]
            flash('Erfolgreich eingeloggt! (Testmodus)', 'success')
            return redirect(url_for('homepage'))

        else:
            flash('Ungültige Anmeldedaten. Bitte versuchen Sie es erneut.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich ausgeloggt.')
    return redirect(url_for('login'))

# ** Geschützter Routen-Decorator **
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Bitte loggen Sie sich zuerst ein.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ** Registrierungsseite mit Passwort-Hashing **
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        prename = request.form['prename']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Benutzername bereits vergeben!', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(prename=prename, lastname=lastname, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrierung erfolgreich! Sie können sich jetzt einloggen.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# ** Datei-Upload-Funktionen **
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_conversion(input_ext, target_ext):
    """Prüft, ob eine Konvertierung innerhalb derselben Dateigruppe möglich ist"""
    if input_ext in IMAGE_FORMATS and target_ext in IMAGE_FORMATS:
        return True
    if input_ext in VIDEO_FORMATS and target_ext in VIDEO_FORMATS:
        return True
    if input_ext in AUDIO_FORMATS and target_ext in AUDIO_FORMATS:
        return True
    if input_ext in DOCUMENT_FORMATS and target_ext in DOCUMENT_FORMATS:
        return True
    return False

def convert_file(filepath, target_format):
    """Simuliert eine Konvertierung durch Umbenennen der Datei"""
    filename, ext = os.path.splitext(os.path.basename(filepath))
    input_format = ext.lstrip('.').lower()

    if not is_valid_conversion(input_format, target_format):
        return None  # Ungültige Konvertierung

    new_filename = f"{filename}_converted.{target_format}"
    converted_path = os.path.join(app.config['CONVERTED_FOLDER'], new_filename)

    # Simulierte Konvertierung: Datei kopieren und umbenennen
    shutil.copy(filepath, converted_path)
    
    return new_filename  # Gibt den neuen Dateinamen zurück

@app.route('/convert')
def convert():
    return render_template('convert.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Keine Datei ausgewählt.', 'error')
        return redirect(url_for('convert'))

    file = request.files['file']
    target_format = request.form.get('format')

    if file.filename == '':
        flash('Keine Datei ausgewählt.', 'error')
        return redirect(url_for('convert'))

    if not target_format or target_format not in ALLOWED_EXTENSIONS:
        flash('Ungültiges oder fehlendes Zielformat.', 'error')
        return redirect(url_for('convert'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Prüfen, ob die Konvertierung erlaubt ist
    input_format = filename.rsplit('.', 1)[1].lower()
    if not is_valid_conversion(input_format, target_format):
        flash(f'Konvertierung von {input_format.upper()} zu {target_format.upper()} nicht erlaubt!', 'error')
        return redirect(url_for('convert'))


        # Datei konvertieren
        converted_filename = convert_file(filepath, target_format)

        if converted_filename:
            flash('Datei erfolgreich konvertiert!', 'success')
            return redirect(url_for('download_file', filename=converted_filename))
        else:
            flash('Konvertierung fehlgeschlagen.', 'error')

    flash('Ungültiger Dateityp.', 'error')
    return redirect(url_for('convert'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)

# ** Admin-Seite **
@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'Administrator':
        flash('Zugriff verweigert: Nur Administratoren dürfen diese Seite aufrufen.', 'error')
        return redirect(url_for('homepage'))
    return render_template('admin.html')

# ** Beispielseiten **
@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/projekte')
def projekte():
    return render_template('projekte.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/soziales')
@login_required
def soziales():
    return render_template('soziales.html')

@app.route('/get_messages')
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).limit(50).all()
    return jsonify([
        {"text": msg.text, "category": msg.category, "timestamp": msg.timestamp.strftime("%H:%M"), "username": msg.username}
        for msg in messages
    ])

@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        return jsonify({"error": "Nicht eingeloggt"}), 403

    text = request.form.get("text")
    category = request.form.get("category", "random")
    username = session.get("username", "Gast")

    if text:
        new_message = ChatMessage(username=username, text=text, category=category)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Nachricht darf nicht leer sein"}), 400

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
