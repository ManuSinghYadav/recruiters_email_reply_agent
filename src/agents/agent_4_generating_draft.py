from pypdf import PdfReader
from pydantic import BaseModel, Field
from agents import Agent

with open("/Users/manuyadav/projects/email_agent/me/summary.txt", "r", encoding="utf-8") as f:
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

Your task is to generate a professional reply for EACH email.

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

- Process EACH email independently
- For each email:
  - Understand the content
  - Draft a professional reply
  - Use only the provided resume and summary as source of truth
  - Do NOT hallucinate missing details

- Maintain a professional, confident tone
- Be concise but informative
- If an email is irrelevant or not job-related, skip it

---

### Output Format (STRICT):

Return in JSON format, which is defined in response format by pydantic class.

- Include only emails that require a reply
- Do NOT include extra text outside JSON
"""


class Drafts(BaseModel):
	id: str = Field(description='Message id of each email.')
	draft: str = Field(description='Email draft which LLM will create.')

class DraftList(BaseModel):
	emails: list[Drafts]


draft_generator_agent = Agent(
	name="draft_generator_agent",
	model='gpt-4o-mini',
	instructions=draft_generator_instruction,
    handoff_description="Generate the draft response for the emails.",
	output_type=DraftList
)