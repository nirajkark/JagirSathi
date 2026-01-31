import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN not found in environment variables")

apify_client = ApifyClient(APIFY_API_TOKEN)


def fetch_linkedIn_jobs(search_query, location="United States", rows=20):
    """Fetch LinkedIn jobs using Apify LinkedIn Jobs Scraper"""

    print(f"[DEBUG] Searching for '{search_query}' in '{location}'")

    run_input = {
        "searchKeywords": search_query,   # ✅ FIXED
        "location": location,
        "maxJobs": rows,                  # ✅ FIXED
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        }
    }

    try:
        run = apify_client.actor(
            "BHzefUZlZRKWxkTck"
        ).call(run_input=run_input)

        dataset_id = run["defaultDatasetId"]
        jobs = list(apify_client.dataset(dataset_id).iterate_items())

        print(f"[DEBUG] Jobs fetched: {len(jobs)}")

        return jobs

    except Exception as e:
        print(f"[ERROR] LinkedIn fetch failed: {e}")
        return []
