from pydantic import BaseModel, Field
from agents import Agent
from src.tools.fetch_full_emails import fetch_full_emails

full_email_fetch_prompt = '''You are responsible for fetching full email content based on filtered email inputs.

You will receive:
A list of relevant emails from the previous agent, each containing:
- msg_id
- subject
- feedback

## Your Task
1. Call the tool `fetch_full_emails`
2. Pass the FULL list of emails exactly as received (do not modify, filter, or recreate)
3. The tool will return full email data (id, subject, body)

## Important Rules
- ALWAYS call the tool if input list is non-empty
- NEVER fabricate or simulate email content
- NEVER skip the tool call
- NEVER change message IDs

## After Tool Execution
Return the result in the required structured format:

{
  "emails": [
    {
      "id": "...",
      "subject": "...",
      "body": "..."
    }
  ]
}

## Edge Case
- If input list is empty → return:
{
  "emails": []
}
and DO NOT call the tool
'''


class FullEmails(BaseModel):
	id: str = Field(description='Message id of each email.')
	subject: str = Field(description='Subject of the email')
	body: str = Field(description='Full email')

class FullEmailsList(BaseModel):
	emails: list[FullEmails]


full_email_fetch_agent = Agent(
   name='full_email_fetch_agent',
	instructions=full_email_fetch_prompt,
	model='gpt-4o-mini',
	tools=[fetch_full_emails],
	handoff_description='Fetch the full emails',
	output_type=FullEmailsList
)