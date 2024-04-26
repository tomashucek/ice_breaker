# code related to getting data from devops

import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

class App():
    
    def run(self):
    # hlavní logika aplikace
        print("Aplikace běží.")
        #logging.info("App running...")
    
        ui = UserIntreface()
        period = ui.get_period()
    
        print(f"\n>>> Processing of data on work items that have been changed between {period[0].date()} to {period[1].date()}\n")
    
        report = DevOpsDataExtractor(*period)
        report_work_items = report.get_items_list()
        #pprint(report_work_items)
        
        try:
            with open("out.txt", "w") as f:
                f.write(f'"role": "system", "content": {system_pgm}\n"role": "user", "content": {user_pgm}\nData period: from "{period[0].date()}" to {period[1].date()}\n')
                json.dump(report_work_items, f, indent=2)
        except Exception as e:
            print(f"Problém se zápisem do souboru {e}")
                
        print(f"\n>>> Loaded data about {len(report_work_items)} work items")

        return None

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
                        AND [System.AreaPath] UNDER '00-DO-PMO\PgM'"""
        
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
  
  

class UserIntreface():
    
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        pass

    def get_period(self) -> list:
        while True:
            try:
                s_date = input("Enter start date: ")
                e_date = input("Enter end date: ")
                
                if s_date == "":
                    s_date = "01-01-2024"
                if e_date == "":
                    e_date = str(datetime.now().strftime("%d-%m-%Y"))
                
                valid_s_date = datetime.strptime(s_date, "%d-%m-%Y")
                valid_e_date = datetime.strptime(e_date, "%d-%m-%Y")
                return [valid_s_date, valid_e_date]
                    
            except ValueError as e:
                print(f"Value error {e}")


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.DEBUG,
                encoding="utf-8",
                filename='app.log', 
                filemode='w', 
                format='%(asctime)s - %(levelname)s - %(message)s')
    
    app = App()
    app.run()
    

