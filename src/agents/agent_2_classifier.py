from pydantic import BaseModel
from agents import Agent, handoff, HandoffInputData
import json
from src.agents.agent_3_full_email_fetch import full_email_fetch_agent

classification_instruction = f"""You are an email classification assistant.

You will receive a list of emails in structured format. Each email contains:
- msg_id: unique identifier
- subject: subject line
- snippet: short preview of the email

## Your Task
Identify ONLY the emails that are relevant to job opportunities or professional communication.

## Criteria for Relevance
Mark an email as relevant ONLY if it clearly includes:
- Messages from recruiters, hiring managers, or HR
- Job opportunities, interview invitations, or follow-ups
- Requests related to job applications (documents, scheduling, etc.)

## Ignore
Do NOT include emails such as:
- Promotions, newsletters, marketing content
- Social media notifications
- Automated updates
- Any non-job-related communication

## Important Rules (STRICT)
- Be highly selective (precision > recall)
- If unsure, EXCLUDE the email
- NEVER include all emails unless ALL are clearly relevant
- It is completely valid to return an empty list

## Handoff Rules (CRITICAL — do not return JSON as your final message)
- If ZERO emails are relevant → reply with plain text: "No relevant emails" and do NOT call any handoff tool
- If one or more emails are relevant → you MUST call the tool `transfer_to_full_email_fetch_agent` with a payload containing ONLY those emails
- Do NOT return classification JSON as your final response — the handoff tool call is how you pass results forward

Each handoff payload email must have:
- msg_id: the Gmail message id
- subject: subject line
- feedback: short reason it is relevant
"""

class EmailResult(BaseModel):
	msg_id: str
	subject: str
	feedback: str

class ClassifierOutput(BaseModel):
	emails: list[EmailResult]


def on_classifier_handoff(ctx, filtered: ClassifierOutput):
    """Required by SDK when input_type is set; no shared state needed."""
    return None


def classifier_handoff_filter(data: HandoffInputData) -> HandoffInputData:
    """Pass only classifier handoff payload to agent 3 (drop full history)."""
    handoff_call = next(
        (item for item in reversed(data.new_items) if getattr(item, "type", "") == "handoff_call_item"),
        None,
    )

    if handoff_call is None:
        return data.clone(input_history=(), pre_handoff_items=(), new_items=())

    payload_json = handoff_call.raw_item.arguments
    return data.clone(
        input_history=({"role": "user", "content": payload_json},),
        pre_handoff_items=(),
        new_items=(),
    )


classifier_agent = Agent(
    name="classifier_agent",
    instructions=classification_instruction,
    model="gpt-4o-mini",
    handoffs=[
        handoff(
            full_email_fetch_agent,
            input_type=ClassifierOutput,
            on_handoff=on_classifier_handoff,
            input_filter=classifier_handoff_filter,
            tool_description_override=(
                "Hand off ONLY recruiter/job emails you classified as relevant. "
                "Pass msg_id, subject, and feedback for each."
            ),
        )
    ],
)