# prohledá devops a najde work item dle zadaného title stringu a vrátí jeho ID
# asi použiju wiql a contains clausuli, ale ještě to chce promyslet

from third_parties import devops


def look_for_work_items(title:str = "nothing") -> list[dict]:
    """Function looks for title of any work items in devops and returns its json data. Input title:str"""

    devops_searcher = devops.DevOpsDataExtractor(title=title)
    list_of_found_items = devops_searcher.get_items_list()
    #print(list_of_found_items)
    return list_of_found_items

def look_for_epic_work_items(title:str = "no Epic") -> list[dict]:
    """Function looks for title of epic work items in devops and returns its json data"""
    
    devops_searcher = devops.DevOpsDataExtractor(title=title, item_types="Epic")
    list_of_found_items = devops_searcher.get_items_list()
    #print(list_of_found_items)
    return list_of_found_items


if __name__ == "__main__":
    look_for_work_items()
