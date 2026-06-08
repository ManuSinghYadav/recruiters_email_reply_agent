from pypdf import PdfReader
from pydantic import BaseModel, Field
from agents import Agent, handoff, ModelSettings
from src.utils.payload_only import payload_builder
from src.agents.agent_5_write_drafts_in_gmail import write_draft_agent

with open(
    "/Users/manuyadav/projects/email_agent/me/summary.txt", "r", encoding="utf-8"
) as f:
    summary = f.read()


reader = PdfReader("/Users/manuyadav/projects/email_agent/me/manu_yadav_cv.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

name = "Manu Yadav"


draft_generator_instruction = f"""
You are acting as {name}, a job candidate communicating with recruiters over email.

You will receive a list of emails. Each email contains:
- id: unique identifier
- body: full email content

Your task is to generate a professional reply for emails. And do not forget to call the handoff in the end.

---

### Candidate Summary:
{summary}

---

### Resume:
{resume}

---

### Emails to Respond:
Input which came from previous tool i.e. fetch_full_emails.

---

### Instructions:

- For each email:
  - Understand the content
  - Draft a professional reply
  - Use only the provided resume and summary as source of truth
  - Do NOT hallucinate missing details

- Maintain a professional, confident tone
- Be concise but informative
- If an email is irrelevant or not job-related, skip it
- Include only emails that require a reply

### Handoff instructions:

- Do not skip the handoff and transfer the results to next agent i.e. write_draft_agent
- Do not call multiple handoffs, but only once when you draft the reply of all emails.
- You MUST have to call the handoff.

"""


class Drafts(BaseModel):
    id: str = Field(description="Message id of each email.")
    draft: str = Field(description="Email draft which LLM will create.")


class DraftList(BaseModel):
    emails: list[Drafts]


draft_generator_on_handoff, draft_generator_input_filter = payload_builder(DraftList)


draft_generator_agent = Agent(
    name="draft_generator_agent",
    model="gpt-4o-mini",
    model_settings=ModelSettings(parallel_tool_calls=False),
    instructions=draft_generator_instruction,
    handoffs=[
        handoff(
            write_draft_agent,
            input_type=DraftList,
            on_handoff=draft_generator_on_handoff,
            input_filter=draft_generator_input_filter,
            tool_description_override=(
                "Call this exactly once after all drafts are generated. "
                "Pass one JSON object with emails as a list containing every draft."
            ),
        )
    ],
)
