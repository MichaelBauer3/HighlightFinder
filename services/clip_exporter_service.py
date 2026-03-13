from pathlib import Path

from clip_exporter import EmailSender
from clip_exporter.drive_runner import DriveRunner


class ClipExporterService:

    def __init__(self, drive_runner: DriveRunner, email_sender: EmailSender):
        self.drive_runner = drive_runner
        self.email_sender = email_sender

    def cleanup_old_folders(self, days_old: int=3) -> None:
        self.drive_runner.cleanup_old_folders(days_old=days_old)

    def upload_folder(self, folder_path: Path) -> str:
        return self.drive_runner.upload_folder(folder_path)

    def send_highlights(self, folders, link) -> None:
        self.email_sender.send_highlights(folders, link)