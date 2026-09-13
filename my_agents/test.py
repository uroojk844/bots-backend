import importlib

from agents import (
    Agent,
    ModelSettings,
    OpenAIChatCompletionsModel,
    Runner,
    SQLiteSession,
    function_tool,
)
from openai import AsyncOpenAI
from models.company import CompanyData
from utils.get_evn import load_env
from utils.md_loader import load_markdown

instructions = load_markdown("instructions/System.md")


ollama_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

Model = load_env("MODEL", "qwen2.5:1.5b")


@function_tool
def getCompanyData(company_id: str) -> CompanyData:
    """
    Get company information about the company using its id and return name and context. If user ask question about any company use this to get company information.
    """
    print(f"Getting info about {company_id}")
    data = load_markdown(f"customers/{company_id}/data.md")
    module = importlib.import_module(f"customers.{company_id}.about")
    about = module.name
    return CompanyData(name=about, context=data)


agent = Agent(
    name="Assistant",
    instructions=instructions,
    model=OpenAIChatCompletionsModel(
        model=Model,
        openai_client=ollama_client,
    ),
    model_settings=ModelSettings(
        temperature=0,
        prompt_cache_options={
            "ttl": "30m",
        },
        # max_tokens=100,
        # reasoning={"effort": "low"},
        # extra_args={"reasoning_effort": "low",},
    ),
    tools=[getCompanyData],
)

session = SQLiteSession("conv")
runner = Runner()


async def ask(query: str, data: CompanyData) -> str:
    result = await runner.run(agent, input=f"{data.name}: {query}", session=session)
    return result.final_output
