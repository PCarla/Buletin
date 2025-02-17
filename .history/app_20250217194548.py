from flask import Flask, request, jsonify
import sqlite3
import smtplib
from email.message import EmailMessage
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# SQLite-Datenbank initialisieren
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO person_data 
            (numele, prenumele, data_nasterii, adresa, cnp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (numele, prenumele, data_nasterii, adresa, cnp)
        )

        conn.commit()
        conn.close()

        # Daten per E-Mail senden
        send_email(numele, prenumele, data_nasterii, adresa, cnp)

        return jsonify({"status": "ok", "message": "Data processed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_field(text, field_name):
    """
    Hilfsfunktion zum Extrahieren eines bestimmten Feldes aus dem Text.
    """
    for line in text.split("\n"):

        if field_name in line:
            return line.split(":")[1].strip()
    return None

def send_email(numele, prenumele, data_nasterii, adresa, cnp):
    """
    E-Mail mit den extrahierten Daten senden.
    """
    email_user = "your_email@gmail.com"

    email_pass = "your_app_password"
    to_email = "recipient@example.com"

    msg = EmailMessage()
    msg["Subject"] = "Extrahierte Personalausweisdaten"
    msg["From"] = email_user
    msg["To"] = to_email
    msg.set_content(f"""
    Numele: {numele}
    Prenumele: {prenumele}
    Data nașterii: {data_nasterii}
    Adresa: {adresa}
    CNP: {cnp}
    """)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
