from pydantic import BaseModel, Field
from agents import function_tool
from src.tools.gmail.gmail_client import GmailClient
import re


class Drafts(BaseModel):
	id: str = Field(description='Message id of each email.')
	draft: str = Field(description='Email draft which LLM will create.')

@function_tool
def extract_info_and_write_draft(drafts: list[Drafts]):

    gmail = GmailClient()

    for i in drafts:
        msg = gmail.service.users().messages().get(
            userId='me',
            id=i.id,
            format='full'
        ).execute()

        thread_id = msg['threadId']

        # Extract Message-ID header (important for reply)
        headers = msg['payload']['headers']
        message_id_header = next(
            (h['value'] for h in headers if h['name'] == 'Message-ID'),
            None
        )

        # Extract sender email (you need this for reply)
        from_header = next(
            (h['value'] for h in headers if h['name'] == 'From'),
            None
        )

        if not message_id_header or not from_header:
            return (f"Missing required headers, skipping email with id: {i.id}")

        # Cleaning the sender email by regex
        to_email = re.search(r'<(.+?)>', from_header)
        to_email = to_email.group(1) if to_email else from_header

        # 
        response = gmail.create_reply_draft(
            to=to_email,
            subject="Interview Opportunity",
            body=i.draft,
            thread_id=thread_id,
            message_id=message_id_header
        )

        return response