import asyncio

from agents import Agent, ModelSettings, Runner, set_default_openai_client
from openai import AsyncOpenAI

from my_agents.test import getCompanyData
from utils.get_evn import load_env
from utils.md_loader import load_markdown

instructions = load_markdown("instructions/System.md")

ollama = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

set_default_openai_client(ollama)

agent = Agent(
    name="Sales agent",
    instructions=instructions,
    model=load_env("MODEL"),
    model_settings=ModelSettings(
        temperature=0,
        max_tokens=100,
    ),
    tools=[getCompanyData],
)


async def main():
    result = await Runner.run(agent, "services, company_id: proficio")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
