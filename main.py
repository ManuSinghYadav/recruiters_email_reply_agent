from src.core.pipeline import run_pipeline
from dotenv import load_dotenv
import asyncio

load_dotenv(override=True)

if __name__ == "__main__":
    result = asyncio.run(run_pipeline())
    print(result)
