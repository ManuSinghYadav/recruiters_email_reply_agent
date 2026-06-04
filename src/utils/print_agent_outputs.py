from agents import RunHooks
import json


class PrintAgentOutputs(RunHooks):
	async def on_agent_start(self, context, agent):
		print(f"\nAgent {agent.name} is running ...")
		
	async def on_llm_end(self, context, agent, response):
		for item in response.output:
			if item.type == 'function_call':
				print(f"Tool invoked: {item.name}")
				print(f"Arguments: {item.arguments}")

				data_dict = json.loads(item.arguments)
				
				if 'emails' in data_dict:
					print(f"Total {len(data_dict['emails'])} emails")
			else:
				print(f"\nFinal output: {item.content[0].text}")
			 
	async def on_agent_end(self, context, agent, output):
		print(f"\nTask Finished")