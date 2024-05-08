# vezme vstupní text -> agent se pokusí identifikovat work item nejvyšší úrovně v DevOps a druhý prompt vrátí summary zajímavá fakta o něm

#The LLM returns a string, while the ChatModel returns a message.

import os
from pprint import pprint
import dotenv
import logging
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from third_parties import devops
from agents import devops_lookup_agent

WI_ID = 36765

def ice_break_with(name: str) -> str:
   
    summary_template = """
    Given the information {work_item_json} about a Azure DevOps work item I want you to create:
    1. report on project progress; note: use latest comments as priority source
    2. identify possible risks
    3. give all names involved including those starting with "Ext -")
    Instructions: output dates as DD.MM.YYYY
    Instructions: format output as markup text
    """
    summary_template_2 = """
    Given the information {work_item_json} about a Azure DevOps work item I want you to create:
    1. item summary
    2. identify possible risks
    3. give all names involved including those starting with "Ext -")
    Instructions: output dates as DD.MM.YYYY
    """
    
    wi_id = devops_lookup_agent.lookup(name) # agent, co najde string "name" v devops a vrátí work item ID nelešpí shody

    if wi_id:
        devops_data_loader = devops.DevOpsDataExtractor() #inicializace devops extraktoru
        wi_data_dict = devops_data_loader.fetch_work_item_data(wi_id, verbose=True)
        summary_prompt_template = PromptTemplate(input_variables=["work_item_json"], template=summary_template) # vytvoří objekt typu PromptTemplate s jednou proměnnou
        openai_llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo") # inicializuje LLM
        chain_new = summary_prompt_template | openai_llm
        result = chain_new.invoke({"work_item_json": wi_data_dict})
        pprint(f"toto je výsledek: \n{result.content}")
    
    else:
        print(f">>> No ID found. Skipping steps")
        result = None

    #chain = LLMChain(llm=openai_llm, prompt = summary_prompt_template) #LLMChain is deprecated
    #result = chain.invoke(input={"work_item_json": wi_data_dict}) #Sputstí chain

    with open("out.md", mode="a", encoding="utf-8") as f_o:
        #json.dump(result, f_o, indent=2)
        try:
            f_o.write(f"##Result text for item {wi_data_dict["ID"]}:{wi_data_dict["Title"]}: \n\n{result.content}")
            f_o.write("\n" *2)
        except TypeError as e:
            print(f"No content to write...\n{e}")




if __name__ == "__main__":
    dotenv.load_dotenv()
    print(f">>> Starting ice_breaker program...")
    

    logging.basicConfig(level=logging.DEBUG,
                encoding="utf-8",
                filename='app.log', 
                filemode='w', 
                format='%(asctime)s - %(levelname)s - %(message)s')

    work_item_description = input("Co budeme hledat?: ")
    ice_break_with(work_item_description)



        
