import importlib
from typing import AsyncIterator

from fastapi.responses import StreamingResponse
from langchain.tools import tool
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

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
# reasoning="low"

llm_with_tools = llm.bind_tools([company_info])


instructions = load_markdown("instructions/System.md")
messages: list[BaseMessage] = [SystemMessage(content=instructions)]

while False:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append(HumanMessage(content=user_input))

    while True:
        response = llm_with_tools.invoke(messages)

        messages.append(response)

        if not response.tool_calls:
            print("AI:", response.content)
            break

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"Running: {tool_name}")
            print(tool_args)

            result = tool_map[tool_name].invoke(tool_args)

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )


def get_info(query: str, company_id: str):
    while True:
        if query.lower() in ["exit", "quit"]:
            break

        messages.append(
            HumanMessage(
                content=f"company_id={company_id}, query={query}",
            ),
        )

        while True:
            response = llm_with_tools.invoke(messages)

            messages.append(response)

            if not response.tool_calls:
                return response.content

            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                print(f"Calling: {tool_name}")

                result = tool_map[tool_name].invoke(tool_args)

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )


company = set()


async def get_info_basic(query: str, company_id: str) -> AsyncIterator[str]:
    if company_id not in company:
        info = company_info.invoke({"company_id": company_id})
        messages.append(HumanMessage(content=f"Company Info:\n{info}"))
        company.add(company_id)

    messages.append(HumanMessage(content=query))

    # response = llm.invoke(messages)
    # messages.append(chunk)

    async for chunk in llm.astream(query):
        if isinstance(chunk.content, str):
            yield chunk.content


def getStream(query: str, company_id: str):
    return StreamingResponse(get_info_basic(query, company_id), media_type="text/plain")
