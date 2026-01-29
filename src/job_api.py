from dotenv import load_dotenv
from langchain_groq import ChatGroq
from apify_client import ApifyClient
import os

load_dotenv()
apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def fetch_linkedIn_jobs(search_query, location="Nepal", rows=30):
    run_input = {
        "title": search_query,
        "location": location,
        "rows": rows,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        }  
    }

    run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())  
    return jobs

