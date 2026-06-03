from src.agents.agent_1_fetch_latest_emails import email_fetch_agent
from agents import trace, Runner
from src.utils.print_agent_outputs import PrintAgentOutputs

async def run_pipeline():
    with trace("Fetching of latest emails"):
        result = await Runner.run(email_fetch_agent, "Fetch the latest emails", hooks=PrintAgentOutputs())

    return result