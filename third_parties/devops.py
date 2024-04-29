# code related to getting data from devops

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication


class DevOpsDataExtractor:
    """ object class that can connect to Azure DevOps and retrieve data about Boards work items"""

    def __init__(self, project_name = "00-DO-PMO", item_types = "Epic") -> None:
        
        load_dotenv(override=True)
        self.organization_url = os.getenv("organization_url")
        self.personal_access_token = os.getenv("personal_access_token")
        self.project_name = os.getenv("project_name")
        self.wit_client = ""
        self.work_items_data = {}
        
        self.wiql = f"""
                    SELECT
                        [System.Id]
                    FROM workitems
                    WHERE
                        [System.TeamProject] = '{project_name}'
                        AND [System.WorkItemType] = '{item_types}'
                        AND [System.AreaPath] UNDER '00-DO-PMO\\PgM'"""
        
        self._api_init()

    def _api_init(self) -> None:

        # Create a connection to the Azure DevOps organization
        credentials = BasicAuthentication("", self.personal_access_token)
        connection = Connection(base_url=self.organization_url, creds=credentials)
    
        # Get a client for the Work Item Tracking service
        self.wit_client = connection.clients.get_work_item_tracking_client()

        return None
    
    def get_items_list(self) -> list[str]:
        """List work items of interest for reporting and read theirs data"""
        
        work_items_data = []
        
        wiql = {"query": self.wiql}
        wiql_results: list[object] = self.wit_client.query_by_wiql(wiql).work_items
        logging.debug(f">>> ➡️ Got {len(wiql_results)} objects as wiql results.....")
        #pprint(wiql_results[0].as_dict())

        for result in wiql_results:
            logging.debug(f">>> Processing: {result.id}")
            wi = self.fetch_work_item_data(result.id)
            work_items_data.append(wi)
        
        return work_items_data
        
    def fetch_work_item_data(self, work_item_id) -> json:
        """Fetches work item's data and returns dictionary of relevant atributes including all comments"""
        
        wi_data = {}
        #logging.debug(f">>> ➡️ Fetching data of {work_item_id} work item..")    
                       
        # Fetch single work item by ID
        
        work_item = self.wit_client.get_work_item(work_item_id, expand = "All").as_dict() # načte data z DevOps do slovníku work_item
        
        #logging.debug(f">>> ➡️ Reading data about {work_item_id} from API.")
    
        comments = self.wit_client.get_comments(self.project_name, work_item_id, top=5).as_dict()
        
        #logging.debug(f">>> ➡️ Coverted data to dict {work_item}")
                
        # zkusit vyčítat i starší revize
        
        wi_data = {
            "ID":           work_item.get("id", None),
            "Title":        work_item.get("fields", {}).get("System.Title", None),
            "State":        work_item.get("fields", {}).get("System.State", None),
            "Assigned to":  work_item.get("fields", {}).get("System.AssignedTo", {}).get("displayName", None),
            "Chagned date": work_item.get("fields", {}).get("System.ChangedDate", None),
            "State chagned":work_item.get("fields", {}).get("Microsoft.VSTS.Common.StateChangeDate", None),
            "Area path":    work_item.get("fields", {}).get("System.AreaPath", None),
            "Sprint":       work_item.get("fields", {}).get("System.IterationPath", None),
            "Start date":   work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.StartDate", None),
            "Target date":  work_item.get("fields", {}).get("Microsoft.VSTS.Scheduling.TargetDate", None),
            "Description":  work_item.get("fields", {}).get("System.Description", None),
            "Tags":         work_item.get("fields", {}).get("System.Tags", None),
            "Comments":     comments
            }
                
        #pprint(wi_data, indent=4)
        
        #logging.info(f">>> ➡️ Logging wi_data: {wi_data}")
        print(f">>> ➡️  Logging wi_data on work_item {wi_data["ID"]}")
        
        
        return wi_data
  

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG,
                encoding="utf-8",
                filename='app.log', 
                filemode='w', 
                format='%(asctime)s - %(levelname)s - %(message)s')
   

    

