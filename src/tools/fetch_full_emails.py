from pydantic import BaseModel
from src.tools.gmail.gmail_client import GmailClient
from agents import function_tool
from src.config.logging import setup_logger


logger = setup_logger(__name__)


class EmailResult(BaseModel):
    msg_id: str
    subject: str
    feedback: str


@function_tool
def fetch_full_emails(emails: list[EmailResult]) -> list[dict]:

    logger.info(f"{len(emails)} emails are relevent.")
    logger.info([{i.subject} for i in emails])
    logger.info("Fetching full emails ...")

    gmail = GmailClient()

    full_emails = []

    for email in emails:
        data = gmail.extract_email_data(email.msg_id)
        full_emails.append(
            {"id": email.msg_id, "subject": data["subject"], "body": data["body"]}
        )

    logger.info(f"{len(full_emails)} full emails fetched")

    return full_emails
