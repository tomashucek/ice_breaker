# very simple script

import os
from pprint import pprint
import pprint as p
import dotenv
import json
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from third_parties import devops

WI_ID = 37127

if __name__ == "__main__":
    dotenv.load_dotenv()
       
    x = os.getenv("OPENAI_API_KEY")

    #prompt = PromptTemplate.from_template("What is a good time for a {adjective} person")
    #prompt.format(adjective = "funny")
     

    summary_template = """
    Given the information {work_item_json} about a Azure DevOps work item I want you to create:
    1. item summary 
    2. identify possible risks
    3. give all names involved (make sure its only human names, sometimes names may start with "Ext -")
    """

    summary_prompt_template = PromptTemplate(input_variables=["work_item_json"], template=summary_template)

    openai_llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    chain = LLMChain(llm=openai_llm, prompt = summary_prompt_template)

    devops_loader = devops.DevOpsDataExtractor()
    wi_dict = devops_loader.fetch_work_item_data(WI_ID)

    result = chain.invoke(input={"work_item_json": wi_dict})

    with open("out.md", mode="a", encoding="utf-8") as f_o:
        #json.dump(result, f_o, indent=2)
        f_o.write(f"##Result text for item {wi_dict["ID"]}:{wi_dict["Title"]}: \n\n{result["text"]}")
        f_o.write("\n" *2)
        
