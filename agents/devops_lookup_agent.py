# úkolem agenta je najít na základě neúplného vstupního stringu nebo slovního popisu kokrétní work item v Azure Devops

import os
from pprint import pprint
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.tools import Tool #Tools are interfaces which help agent to interact with external word
from langchain.agents import (
    create_react_agent,
    AgentExecutor,
)
from langchain import hub
from tools.tools import look_for_work_items

# the power of langchain is that it can turn any py function into a tool and make it available for LLM

def lookup(work_item_title: str) -> str:

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-3.5-turbo",
    )

    template = """
            Input: the description or approximate name {wi_name} of the work item name; try so improve input string before using your tool to increase the chance of success
            Task: I want you to get me the id and url of the devops board work item
            Context: your search tool is based on Wiql query "contains input" so may result in multiple or zero matches. You need to retry search with updated input string. Your search tool returs json data with url in it.
            Your final answer schema -> list[ID, url]"""

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["wi_name"]
    )

    react_prompt = hub.pull("hwchase17/react")
    #pprint(react_prompt)
    
    tools_for_agent= [
        Tool(
            name = "Search for Azure DevOps Boards work items",
            func=look_for_work_items,
            description = "useful when you need to get info about work items from azure devops work based on its approximate name.",
        )
    ]

    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(wi_name = work_item_title)}
    )

    #print(result["output"])

    return result["output"]


if __name__ == "__main__":
    print("Starting program...")
    devops_wi_url = lookup(work_item_title="cci")
    print(devops_wi_url)