from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import base64
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from src.config.logging import setup_logger


logger = setup_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailClient:
    """Handles all major Gmail API functions"""

    def __init__(self) -> None:
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        creds = None

        if os.path.exists("token.pkl"):
            with open("token.pkl", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/manuyadav/projects/email_agent/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

            with open("token.pkl", "wb") as token:
                pickle.dump(creds, token)

        return build("gmail", "v1", credentials=creds)

    # This is to read emails.
    def extract_email_data(self, msg_id):
        msg = (
            self.service.users()
            .messages()
            .get(userId="me", id=msg_id, format="full")
            .execute()
        )

        payload = msg["payload"]
        headers = payload.get("headers", [])

        # -----------------------
        # ID and Subject
        # -----------------------
        msg_id = msg["id"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")

        # -----------------------
        # Snippet (easy win)
        # -----------------------
        snippet = msg.get("snippet", "")

        # -----------------------
        # Extract full body
        # -----------------------
        def get_body(payload):
            mime = payload.get("mimeType", "")
            body = payload.get("body", {})

            if mime == "text/plain" and "data" in body:
                return body["data"], "plain"

            if mime == "text/html" and "data" in body:
                return body["data"], "html"

            for part in payload.get("parts", []):
                result = get_body(part)
                if result:
                    return result

            return None

        result = get_body(payload)

        full_text = ""

        if result:
            data, body_type = result

            decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

            if body_type == "html":
                soup = BeautifulSoup(decoded, "html.parser")
                full_text = soup.get_text(separator="\n")
            else:
                full_text = decoded

        return {
            "id": msg_id,
            "subject": subject,
            "snippet": snippet,
            "body": full_text.strip(),
        }

    # This is to send email.
    def send_email(self, to, subject, body):
        message = MIMEText(body)

        message["to"] = to
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        message = {"raw": raw}

        self.service.users().messages().send(userId="me", body=message).execute()

        logger.info("Email sent!")

    # This to write drafts (this will be called by function tool)

    def create_reply_draft(self, to, subject, body, thread_id, message_id):
        try:
            message = MIMEText(body)

            message["to"] = to
            message["subject"] = f"Re: {subject}"
            message["In-Reply-To"] = message_id
            message["References"] = message_id

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            draft = {"message": {"raw": raw, "threadId": thread_id}}

            self.service.users().drafts().create(userId="me", body=draft).execute()

            return {"is_draft_written": True}

        except Exception as e:
            return {"is_draft_written": False, "Error": str(e)}
