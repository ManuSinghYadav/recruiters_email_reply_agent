from pydantic import BaseModel
from src.tools.gmail.gmail_client import GmailClient
from agents import function_tool

class EmailResult(BaseModel):
	msg_id: str
	subject: str
	feedback: str
	
@function_tool
def fetch_full_emails(emails: list[EmailResult]) -> list[dict]:

    print(f"{len(emails)} emails are relevent.")
    print([{i.subject} for i in emails])
    print("Fetching full emails ...")
    
    msg_ids = [e.msg_id for e in emails]
	
    gmail = GmailClient()

    query = "is: newer_than:2d -category:promotions -category:social"

    results = gmail.service.users().messages().list(
        userId='me',
        q=query,
        maxResults=10
    ).execute().get('messages', [])

    emails = []

    for m in results:
      if m['id'] in msg_ids:
        data = gmail.extract_email_data(m['id'])
        emails.append({
            "id": m["id"],
            "subject": data["subject"],
				"body": data["body"]
        })
	
    print("Full emails fetched")

    return emails