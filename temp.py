from pydantic import BaseModel, Field
from langchain.tools import tool
from third_parties import devops
from pprint import pprint


item = devops.DevOpsDataExtractor()

x = item.fetch_work_item_data(work_item_id=36749, verbose=False)

print(f"This is content: \n{x}")


