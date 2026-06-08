from src.tools.gmail.gmail_client import GmailClient
from agents import function_tool
from src.config.logging import setup_logger


logger = setup_logger(__name__)


@function_tool
def fetch_latest_emails() -> list[dict]:
    logger.info("Fetching latest emails")

    gmail = GmailClient()

    query = "is: newer_than:2d -category:promotions -category:social -category:updates"

    results = (
        gmail.service.users()
        .messages()
        .list(userId="me", q=query, maxResults=10)
        .execute()
        .get("messages", [])
    )

    emails = []

    for m in results:
        data = gmail.extract_email_data(m["id"])

        emails.append(
            {
                "msg_id": m["id"],
                "subject": data["subject"],
                "snippet": data["snippet"],
            }
        )

    logger.info(f"{len(emails)} emails fetched.")
    logger.info([f"Subject: {i['subject']}" for i in emails])

    return emails
