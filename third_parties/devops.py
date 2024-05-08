# code related to getting data from devops

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from pprint import pprint

MAX_ITEMS_TO_LOOKFOR = 21 #if search returns too many work items, it can overload LLMs context window

class DevOpsDataExtractor:
    """ object class that can connect to Azure DevOps and retrieve data about Boards work items"""

    def __init__(self, project_name = "00-DO-PMO", item_types = "Any", title = "") -> None:
        
        load_dotenv(override=True)
        self.organization_url = os.getenv("organization_url")
        self.personal_access_token = os.getenv("personal_access_token")
        self.project_name = project_name
        self.item_types = item_types
        self.wit_client = ""
        self.work_item_title = title
        self.work_items_ids = []
        
        sign = self._evaluate_item_type(item_types)

        self.wiql = f"""
                    SELECT
                        [System.Id],
                        [System.WorkItemType],
                        [System.State],
                        [System.Tags]
                    FROM workitems
                    WHERE
                        [System.TeamProject] = '{self.project_name}'
                        AND [System.Title] CONTAINS '{self.work_item_title}'
                        AND [System.WorkItemType] {sign}"""
        
        pprint(f"Toto je wiql query:\n{self.wiql}")

        self._api_init()

    def _api_init(self) -> None:

        # Create a connection to the Azure DevOps organization
        credentials = BasicAuthentication("", self.personal_access_token)
        connection = Connection(base_url=self.organization_url, creds=credentials)
    
        # Get a client for the Work Item Tracking service
        self.wit_client = connection.clients.get_work_item_tracking_client()

        return None

    # Getter for work_item_title
    @property
    def work_item_title(self):
        print("Entered getter")
        return self._work_item_title
    
    # Setter for work_item_title
    @work_item_title.setter
    def work_item_title(self, title):
        print(f"\nEntering setter for work_item_title: {title}")
        print(f"Setting _work_item_title to {title}")
        self._work_item_title = title
        return None
        

    def _evaluate_item_type(self, item_types):
        
        item_types_options = ["Any", "Epic", "Feature", "Story"]
        
        if item_types in item_types_options:
            match item_types:
                case "Any":
                    return "<> 'Any'"
                case "Feature":
                    return "= 'Feature'"
                case "Epic":
                    return "= 'Epic'"
                case "Story":
                    return "= 'User Story'"
                case _:
                    return "<> ''"
                


    def get_items_list(self) -> list[dict]:
        """Looks for work items whose Title in DevOps contains self.title: str and returns list of found items"""
        
        work_items_data = []
        
        wiql = {"query": self.wiql}
        #pprint(f"🔴Toto je wiql, co jde do devops:\n{wiql}")

        wiql_results: list[object] = self.wit_client.query_by_wiql(wiql).work_items
        logging.debug(f">>> ➡️ Got {len(wiql_results)} objects as wiql results.....")
        #pprint(wiql_results[0].as_dict())

        if len(wiql_results) < MAX_ITEMS_TO_LOOKFOR: #pokud načítám už 20 wi, tak je můj search string špatně

            for result in wiql_results:
                logging.debug(f">>> Processing: {result.id}")
                data = self.fetch_work_item_data(result.id, verbose=False)
                work_items_data.append(data)
            
            return work_items_data
        else:
            return "Too many results, try to be more specific"
        
    def fetch_work_item_data(self, work_item_id:str, verbose=True) -> json:
        """Fetches work item's data and returns dictionary of relevant atributes. If verbose=True, then including all comments and some other atributes"""
        
        if work_item_id:

            try: 
                id = int(work_item_id)
            except ValueError as e:
                print(f"ValueError when converting id to integer. ID={work_item_id}\n{e}")
                return [0]
            
            except TypeError as e:
                print(f"TypeError when converting id to integer. ID={work_item_id}\n{e}")
                return [0]

            wi_data = {}
            logging.debug(f">>> ➡️ Fetching data of {id} work item..")    
                       
            # Fetch single work item by ID
            work_item = self.wit_client.get_work_item(id, expand = "All").as_dict() # načte data z DevOps do slovníku work_item
            
            logging.debug(f">>> ➡️ Reading data about {id} from API.")
            comments = self.wit_client.get_comments(self.project_name, id, top=15).as_dict()
            logging.debug(f">>> ➡️ Coverted data to dict {work_item}")
        else:
            return "No ID provided, thus nothing can be returend"

        # zkusit vyčítat i starší revize
        
        if verbose:
            wi_data = {
                "ID":           work_item.get("id", None),
                "Title":        work_item.get("fields", {}).get("System.Title", None),
                "State":        work_item.get("fields", {}).get("System.State", None),
                "Type":         work_item.get("fields", {}).get("System.WorkItemType", None),
                "Assigned to":  work_item.get("fields", {}).get("System.AssignedTo", {}).get("displayName", None),
                "Chagned date": work_item.get("fields", {}).get("System.ChangedDate", None),
                "State chagned":work_item.get("fields", {}).get("Microsoft.VSTS.Common.StateChangeDate", None),
                "Area path":    work_item.get("fields", {}).get("System.AreaPath", None),
                "Sprint":       work_item.get("fields", {}).get("System.IterationPath", None),
                "Start date":   work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.StartDate", None),
                "Target date":  work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.TargetDate", None),
                "Description":  work_item.get("fields", {}).get("System.Description", None),
                "Tags":         work_item.get("fields", {}).get("System.Tags", None),
                "url":          work_item.get("url", {}),
                "Comments":     comments
                }
        else:
            wi_data = {
                "ID":           work_item.get("id", None),
                "Title":        work_item.get("fields", {}).get("System.Title", None),
                "State":        work_item.get("fields", {}).get("System.State", None),
                "Type":         work_item.get("fields", {}).get("System.WorkItemType", None),
                "Assigned to":  work_item.get("fields", {}).get("System.AssignedTo", {}).get("displayName", None),
                "Chagned date": work_item.get("fields", {}).get("System.ChangedDate", None),
                "Area path":    work_item.get("fields", {}).get("System.AreaPath", None),
                "Start date":   work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.StartDate", None),
                "Target date":  work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.TargetDate", None),
                "Tags":         work_item.get("fields", {}).get("System.Tags", None),
                "url":          work_item.get("url", {})
                }

        #pprint(wi_data, indent=4)
        
        logging.info(f">>> ➡️ Logging wi_data: {wi_data}")
        print(f">>> ➡️  Logging wi_data on work_item {wi_data["ID"]}")
        
        return wi_data
  

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG,
                encoding="utf-8",
                filename='app.log', 
                filemode='a', 
                format='%(asctime)s - %(levelname)s - %(message)s')
   

    

