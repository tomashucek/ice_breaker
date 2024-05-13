# úkolem agenta je najít na základě neúplného vstupního stringu nebo slovního popisu kokrétní work item v Azure Devops
from pprint import pprint
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
#from langchain_core.tools import Tool #Tools are interfaces which help agent to interact with external word
from langchain.agents import (
    create_react_agent,
    AgentExecutor,
)
from langchain import hub
from tools.tools import look_for_work_items, look_for_work_epic_items

# the power of langchain is that it can turn any py function into a tool and make it available for LLM


def lookup(look_for: str) -> str:

    llm = ChatOpenAI(
        temperature=0,
        #model_name="gpt-3.5-turbo-0125",
        model_name="gpt-4o"
    )

    template_ai_updated = """
            Input: the work item name or a close approximation: {wi_name}. Optimize this input string before using it to increase the success rate of your search.
            Task: Retrieve the ID of a specific work item from the DevOps board.
            Context: Your search is powered by a WiQL query that includes the "contains" condition, which might return multiple or zero matches. Adjust and refine the input string if the initial search is unsuccessful.
            Instructions: 
                1. Use the input string to perform a WiQL query. Parse the returned JSON data to find the work item IDs. 
                2. If multiple matches are found, prioritize the highest level of the hierarchy: Epic > Feature > User Story/Issue > Task/Bug.
                3. Return the ID of the highest-priority work item.
            Output Format: Return the work item ID as an integer (Example: 11111)
            """

    template_backub = """
            Input: the description or approximate name of the work item name: {wi_name}; try so improve input string before using your tool to increase the chance of success
            Context: your search tools are based on Wiql query "contains input" so may result in multiple or zero matches. You need to retry search with updated input string. Your search tool returs json data with ID in it.
            Task: I want you to get me the id of the devops board work item
            Instructions: if you find more than one match, analyse recieved data and output the highest level work item. Pick one. Hirarchy goes Epic -> Feature -> User Story/Issue -> Task/Bug.
            Your final answer -> int(ID)"""

    template = """
            Context: You are an AI agent that searches the JSON data it receives using its tools for the most likely match to the input text. Your search tools are based on the Wiql query "contains", which looks in the Work item title field. Search may result in multiple or zero matches. You need to retry search with updated input string.

            Task: your task is to use the tools to find the Azure DevOps work item that most likely matches the user-supplied string and get its unique ID number.

            Instructions: 
                1) identify keywords or phrases in the input string and use it to search
                2) your action input must be plain string!!!!
                3) if there is EPIC type in dataset, extract and output its ID
                4) output only the ID
                Note: the top-down hierarchy of work items looks like this: Epic - Feature - User Story/Issue - Task/Bug
                4) if more than one option matches the assignment, prioritize those higher in the hierarchy

            Input: This is the input string from the user: {wi_name};
            
            Your final answer must have numeric format. Example 11111"""
   

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["wi_name"]
    )

    react_prompt = hub.pull("hwchase17/react")
    #pprint(react_prompt)
    print("working on tools for agent")
    
    tools_for_agent = [look_for_work_items, look_for_work_epic_items]

    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools_for_agent, verbose=True)

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(wi_name = look_for)}
    )

    #print(result["output"])

    #query = "what is devops id of item called keepl? Use tool to find out"

    #llm_with_tools = llm.bind_tools(tools_for_agent)
    #result = llm_with_tools.invoke(query)
    #pprint(result)

    return result["output"]


if __name__ == "__main__":
    print(">>> Starting devops_lookup_agent...")
    devops_wi_url = lookup("I am looking for info related to keepl")
    #print(devops_wi_url)