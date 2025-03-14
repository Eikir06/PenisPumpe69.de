from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# ** Secret Key für Sessions & Flash Messages **
app.secret_key = 'supersecretkey'

# ** SQLite-Datenbank einbinden **
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ** Datenbank-Modelle definieren **
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prename = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Passwort wird jetzt gehasht gespeichert!

# ** Datenbank erstellen, falls nicht vorhanden **
with app.app_context():
    db.create_all()

@app.route('/')
def homepage():
    return render_template('index.html')  # Startseite auf '/' setzen

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Benutzer aus der SQLite-Datenbank abrufen
        user = User.query.filter_by(username=username).first()

        # Passwortprüfung mit Hashing
        if user and check_password_hash(user.password, password):  
            session['logged_in'] = True
            session['username'] = user.username  # Username in Session speichern
            flash('Erfolgreich eingeloggt!', 'success')
            return redirect(url_for('homepage'))
        else:
            flash('Ungültige Anmeldedaten. Bitte versuchen Sie es erneut.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Sitzung zurücksetzen
    flash('Sie wurden erfolgreich ausgeloggt.')
    return redirect(url_for('login'))

# ** Geschützter Routen-Decorator **
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):  # Wenn der Benutzer nicht eingeloggt ist
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

        # Prüfen, ob der Benutzername bereits existiert
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Benutzername bereits vergeben!', 'error')
            return redirect(url_for('register'))

        # Passwort hashen & Benutzer speichern
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(prename=prename, lastname=lastname, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrierung erfolgreich! Sie können sich jetzt einloggen.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

