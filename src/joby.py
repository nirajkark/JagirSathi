import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
apify_client = ApifyClient(APIFY_API_TOKEN)

def fetch_linkedIn_jobs(search_query: str, location: str = "United States", rows: int = 10):
    if not search_query:
        return []

    # Using the standard LinkedIn Jobs Scraper actor
    run_input = {
        "queries": [f"{search_query} in {location}"],
        "maxItems": rows,
    }

    try:
        # Check actor ID: BHzefUZlZRKWxkTck is the standard one
        run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
        
        normalized_jobs = []
        for job in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
            normalized_jobs.append({
                "title": job.get("title") or job.get("positionName"),
                "company": job.get("companyName") or job.get("company"),
                "location": job.get("location"),
                "link": job.get("jobUrl") or job.get("link"),
            })
        return normalized_jobs
    except Exception as e:
        print(f"Scraper error: {e}")
        return []