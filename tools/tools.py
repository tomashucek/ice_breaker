# prohledá devops a najde work item dle zadaného title stringu a vrátí jeho ID
# asi použiju wiql a contains clausuli, ale ještě to chce promyslet

from third_parties import devops


def look_for_work_items(title:str = "nothing"):
    """Function looks for title of the work item in devops and returns its ID"""

    devops_searcher = devops.DevOpsDataExtractor(title=title)
    list_of_found_items = devops_searcher.get_items_list()
    print(list_of_found_items)
    return list_of_found_items

if __name__ == "__main__":
    look_for_work_items()
