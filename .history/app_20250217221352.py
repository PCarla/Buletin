from flask import Flask, request, jsonify
import sqlite3
import smtplib
from email.message import EmailMessage
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

# Laden der Umgebungsvariablen
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    logger.info("Initializing Flask application...")
    app = Flask(__name__)
    CORS(app)

    # SQLite-Datenbank initialisieren
    def init_db():
        logger.info("Initializing database...")
        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS person_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numele TEXT,
                    prenumele TEXT,
                    data_nasterii TEXT,
                    adresa TEXT,
                    cnp TEXT
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
        finally:
            conn.close()

    init_db()

    @app.route("/process_text", methods=["POST"])
    def process_text():
        logger.info("Processing request at /process_text")
        try:
            # JSON-Daten empfangen
            data = request.json
            if not data or "text" not in data:
                logger.error("No text provided in the request.")
                return jsonify({"error": "No text provided"}), 400

            extracted_text = data["text"]

            # Parsing der Daten
            numele = extract_field(extracted_text, "Numele")
            prenumele = extract_field(extracted_text, "Prenumele")
            data_nasterii = extract_field(extracted_text, "Data nașterii")
            adresa = extract_field(extracted_text, "Adresa")
            cnp = extract_field(extracted_text, "CNP")

            # Überprüfen, ob alle Felder extrahiert wurden
            if not all([numele, prenumele, data_nasterii, adresa, cnp]):
                logger.error("Failed to extract all required fields.")
                return jsonify({"error": "Failed to extract all required fields"}), 400

            # Daten in die Datenbank einfügen
            try:
                conn = sqlite3.connect("data.db")
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO person_data (
                        numele,
                        prenumele,
                        data_nasterii,
                        adresa,
                        cnp
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (numele, prenumele, data_nasterii, adresa, cnp)
                )
                conn.commit()
                logger.info("Data successfully inserted into the database.")
            except sqlite3.Error as e:
                logger.error(f"Database error: {e}")
                return jsonify({"error": "Database error"}), 500
            finally:
                conn.close()

            # Daten per E-Mail senden
            send_email(numele, prenumele, data_nasterii, adresa, cnp)

            return jsonify({"status": "ok", "message": "Data processed successfully"})
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
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
        email_user = os.getenv("EMAIL_USER")
        email_pass = os.getenv("EMAIL_PASS")
        to_email = os.getenv("TO_EMAIL")
        if not email_user or not email_pass or not to_email:
            logger.error("Email credentials are not set in environment variables.")
            return

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

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(email_user, email_pass)
                smtp.send_message(msg)
            logger.info("Email sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=8080)
