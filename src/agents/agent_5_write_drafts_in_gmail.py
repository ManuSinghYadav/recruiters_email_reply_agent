from agents import Agent
from src.tools.write_drafts_in_gmail import extract_info_and_write_draft

write_draft_instruction = """You are an execution agent.

Your only responsibility is to create a draft reply email using the provided tool.

You will receive:
- msg_id: the ID of the email to reply to
- draft: the reply content to be written

Instructions:

1. Call the tool `extract_info_and_write_draft`
2. Pass the FULL list of draft exactly as received (do not modify, filter, or recreate)
3. Do NOT modify, analyze, or rewrite the draft content.
4. Simply return if draft is written in email or not.

Important rules:
- Do NOT generate or change the draft text
- Do NOT skip the tool call
- Do NOT add explanations or extra text
- Your job is only to execute the tool call with the given inputs"""


write_draft_agent = Agent(
    name="write_draft_agent",
    model="gpt-4o-mini",
    instructions=write_draft_instruction,
    tools=[extract_info_and_write_draft],
    handoff_description="Execute the tool",
)
