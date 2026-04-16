import logging
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config import SENDER_EMAIL_ADDRESS, SENDER_EMAIL_PASSWORD, SEND_TO_EMAIL_ADDRESS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class EmailSender:

    SMTP_ADDRESS = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self):
        self.email = SENDER_EMAIL_ADDRESS
        self.password = SENDER_EMAIL_PASSWORD
        self.to = SEND_TO_EMAIL_ADDRESS

    def send_highlights(self, folders, link):
        """Builds and sends the highlights clip_exporter."""

        subject, body = self._build_email_content(folders, link)
        self._send(subject, body, link)

    def _build_email_content(self, valid_folders, link):
        """Builds subject and body from folder names."""
        lines = []
        for folder in valid_folders:
            team_name, goal_count = self._parse_folder(folder)
            lines.append(f"{team_name} Scored {goal_count} Goal(s), Highlights Attached.")

        lines.append(f"Link to Drive: {link}")

        subject = "RSG Highlights"
        body = "\n".join(lines)

        return subject, body

    def _send(self, subject, body, folder_paths):
        """Builds the MIME message and sends it."""

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.to
        msg['Cc'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:

            with smtplib.SMTP_SSL(self.SMTP_ADDRESS, self.SMTP_PORT) as server:

                server.login(self.email, self.password)
                server.sendmail(self.email, self.to, msg.as_string())
            logging.info(f"Email sent successfully with {len(folder_paths)} folder(s).")

        except smtplib.SMTPAuthenticationError:
            logging.error("Authentication failed. Check your clip_exporter/password in config.")
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send clip_exporter: {e}")

    @staticmethod
    def _parse_folder(folder_path):
        """
        Parses folder name formatted as <TEAM NAME>_<GAME DATE>_HL.
        Returns (team_name, goal_count).
        Goal count is determined by the number of .mp4 files in the folder.
        """
        folder_name = os.path.basename(folder_path)
        parts = folder_name.split('_')
        team_name = parts[0] + " " + parts[1] if parts else "Unknown Team"

        goal_count = sum(1 for f in os.listdir(folder_path) if f.endswith('.mp4'))
        return team_name, goal_count
