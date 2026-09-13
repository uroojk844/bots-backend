import importlib
from typing import AsyncIterator

from langchain.tools import tool
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from models.company import CompanyData
from utils.get_evn import load_env
from utils.md_loader import load_markdown


@tool
def company_info(company_id: str) -> CompanyData:
    """
    Get company information about the company using its id and return name and context. If user ask question about any company use this to get company information.
    """
    print(f"Getting info about {company_id}")
    data = load_markdown(f"customers/{company_id}/data.md")
    module = importlib.import_module(f"customers.{company_id}.about")
    about = module.name
    return CompanyData(name=about, context=data)


tool_map = {"company_info": company_info}

model = load_env("MODEL")

llm = ChatOllama(
    model=model,
    temperature=0,
)

instructions = load_markdown("instructions/System.md")
messages: list[BaseMessage] = [SystemMessage(content=instructions)]

company = dict()
current = ""


async def get_info_basic(query: str, company_id: str) -> AsyncIterator[str]:
    global current

    if current != company_id:
        del messages[1:]

        info = company.get(company_id, company_info.invoke({"company_id": company_id}))
        messages.append(HumanMessage(content=f"Company Info:\n{info}"))
        company[company_id] = info
        current = company_id

        print(messages)

    messages.append(HumanMessage(content=query))

    chunks = []
    async for chunk in llm.astream(messages):
        if isinstance(chunk.content, str):
            chunks.append(chunk.content)
            yield chunk.content

    full_response = "".join(chunks)

    messages.append(AIMessage(content=full_response))
