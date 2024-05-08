# prohledá devops a najde work item dle zadaného title stringu a vrátí jeho ID
# asi použiju wiql a contains clausuli, ale ještě to chce promyslet

from pydantic import BaseModel, Field
from third_parties import devops
from langchain.tools import tool


@tool
def look_for_work_items(search_str: str) -> list[dict]:
    """Generic search. The function looks up the search_str string of a work item in Azure DevOps based on its Title"""
    search_str = search_str.strip().casefold()
    devops_searcher = devops.DevOpsDataExtractor(title=search_str)
    list_of_found_items = devops_searcher.get_items_list()
    
    return list_of_found_items

@tool
def look_for_work_epic_items(search_str: str) -> list[dict]:
    """Epic search. The function looks up the search_str string of a work item of type epic in Azure DevOps based on its Title"""
    search_str = search_str.strip().casefold()
    
    devops_searcher = devops.DevOpsDataExtractor(title=search_str, item_types="Epic")
    list_of_found_items = devops_searcher.get_items_list()
    
    return list_of_found_items



if __name__ == "__main__":
    #look_for_work_items(title="cci", item_type="Any"])
    print(look_for_work_items.name, "\n")
    print(look_for_work_items.description, "\n")
    print(look_for_work_items.return_direct, "\n")
    print(look_for_work_items.args)

