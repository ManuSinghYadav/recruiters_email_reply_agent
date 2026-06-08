from agents import RunHooks
import json
from src.config.logging import setup_logger


logger = setup_logger(__name__)


class PrintAgentOutputs(RunHooks):
    async def on_agent_start(self, context, agent):
        logger.info(f"Agent {agent.name} is running ...")

    async def on_llm_end(self, context, agent, response):
        for item in response.output:
            if item.type == "function_call":
                logger.info(f"Tool invoked: {item.name}")
                logger.info(f"Arguments: {item.arguments}")

                data_dict = json.loads(item.arguments)

                if "emails" in data_dict:
                    logger.info(f"Total {len(data_dict['emails'])} emails\n")
            else:
                logger.info(f"Final output: {item.content[0].text}\n")

    async def on_agent_end(self, context, agent, output):
        logger.info("Task Finished")
