import requests
import json
import sys
import time
from datetime import datetime
from collections import Counter

def generate_tld_query(tld_count=50):
    try:
        url = "https://isc.sans.edu/api/recentdomains?json"
        print(f"Making request to: {url}")
        
        # Add a longer initial delay
        print("Waiting 15 seconds before making request...")
        time.sleep(15)
        
        max_retries = 3
        retry_count = 0
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        while retry_count < max_retries:
            start_time = time.time()
            response = requests.get(url, headers=headers)
            elapsed_time = time.time() - start_time
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Request took {elapsed_time:.2f} seconds")
            
            # Try to parse the response regardless of content-type
            try:
                # Wait if response was too quick
                if elapsed_time < 10:
                    wait_time = 10 - elapsed_time
                    print(f"Response was too quick, waiting {wait_time:.2f} more seconds...")
                    time.sleep(wait_time)
                
                # Try to parse the response
                data = response.json()
                if data:
                    print("Successfully parsed JSON response")
                    break
                else:
                    print("Empty JSON response")
            except json.JSONDecodeError:
                print(f"Failed to parse JSON (attempt {retry_count + 1}/{max_retries})")
                print(f"Response preview: {response.text[:200]}...")
                
                # If we got HTML, wait longer and retry
                print("Waiting 20 seconds before retrying...")
                time.sleep(20)
                retry_count += 1
                continue
        
        if retry_count == max_retries:
            print("Max retries reached. Could not get JSON response.")
            return
            
        # Extract TLDs and count their occurrences
        tlds = [domain["domainname"].split(".")[-1] for domain in data if domain["domainname"]]
        tld_counts = Counter(tlds)
        
        # Get top N TLDs
        top_tlds = [tld for tld, _ in tld_counts.most_common(tld_count)]
        
        query = f"""EmailEvents
| where RecipientEmailAddress endswith ({' or '.join(f'"{tld}"' for tld in top_tlds)})
| summarize count() by RecipientEmailAddress, SenderFromAddress, Subject
| order by count_ desc"""

        # Save the query to a .txt file
        with open("tld_query.txt", "w") as f:
            f.write(query)
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    tld_count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    generate_tld_query(tld_count) 