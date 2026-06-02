from pydantic import BaseModel, Field
from agents import Agent, handoff
from src.utils.payload_only import payload_builder
from src.tools.fetch_full_emails import fetch_full_emails
from src.agents.agent_4_generating_draft import draft_generator_agent


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
4. Call the handoff

## Important Rules
- ALWAYS call the tool if input list is non-empty
- NEVER fabricate or simulate email content
- NEVER skip the tool call
- NEVER change message IDs
- NEVER skip handoff and always handoff all the emails, dont skip any email which handoff.

## After Tool Execution
Run the handoff and pass the required output.

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


on_full_email_handoff, full_email_handoff_filter = payload_builder(FullEmailsList)


full_email_fetch_agent = Agent(
   name='full_email_fetch_agent',
	instructions=full_email_fetch_prompt,
	model='gpt-4o-mini',
	tools=[fetch_full_emails],
	handoffs=[
        handoff(
            draft_generator_agent,
            input_type=FullEmailsList,
            on_handoff=on_full_email_handoff,
            input_filter=full_email_handoff_filter,
            tool_description_override=(
					 "Hand off full email to next agent"
					 "Pass id, subject, and body for each"
            ),
        )
    ],
	handoff_description='Fetch the full emails and call the handoff.',
)