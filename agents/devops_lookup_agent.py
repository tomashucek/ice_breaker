
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


# the power of langchain is that it can turn any py function into a tool and make it available for LLM

def lookup(work_item_title: str) -> str:

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-3.5-turbo",
    )

    template = """given the name of work item {wi_name} I want you to get me its devops board work item url. Your answer should contain only a URL"""

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["wi_name"]
    )

    react_prompt = hub.pull("hwchase17/react")
    pprint(react_prompt)
    
    tools_for_agent= [
        Tool(
            name = "Search for Azure DevOps Boards work items",
            func="?",
            description = "useful when you need to get the ID of an azure devops work item based on its approximate name.",
        )
    ]



    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(wi_name = work_item_title)}
    )

    devops_item_id = result["id"]

    return devops_item_id


if __name__ == "__main__":
    devops_wi_url = lookup(work_item_title="CCI_rebuild")
    #print(devops_wi_url)
    ...