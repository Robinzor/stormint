from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta
from collections import Counter
from functools import lru_cache
import time
import json

app = Flask(__name__)

ITEMS_PER_PAGE = 20
CACHE_TIMEOUT = 300  # 5 minutes in seconds
TOP_PORTS_LIMIT = 100  # Number of top ports to fetch
TOP_TLDS_LIMIT = 10  # Number of top TLDs to fetch

# Cache for API responses
@lru_cache(maxsize=32)
def cached_fetch_sans_data():
    url = "https://isc.sans.edu/api/recentdomains?json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


@lru_cache(maxsize=32)
def cached_fetch_top_ips():
    url = "https://isc.sans.edu/api/topips?json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching top IPs: {e}")
        return []

@lru_cache(maxsize=32)
def cached_fetch_top_ports(limit=100):
    url = f"https://isc.sans.edu/api/topports/records/{limit}?json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # The data is a dictionary where keys are string numbers
        ports = []
        for key, port_data in data.items():
            if key != 'date' and key != 'limit':  # Skip metadata fields
                ports.append({
                    'rank': str(port_data.get('rank', '')),
                    'port': str(port_data.get('targetport', '')),
                    'records': int(port_data.get('records', 0)),
                    'targets': int(port_data.get('targets', 0)),
                    'sources': int(port_data.get('sources', 0))
                })
        # Sort by rank
        ports.sort(key=lambda x: int(x['rank']) if x['rank'].isdigit() else 0)
        return ports
    except requests.RequestException as e:
        print(f"Error fetching top ports: {e}")
        return []
    except (ValueError, TypeError) as e:
        print(f"Error parsing port data: {e}")
        return []

def fetch_sans_data():
    return cached_fetch_sans_data()

def fetch_top_ips():
    return cached_fetch_top_ips()

def fetch_top_ports(limit=100):
    return cached_fetch_top_ports(limit)

def analyze_data(data, tld_limit=10):
    if not data:
        return {}
    
    # Count types
    type_counts = Counter(item.get('type', 'unknown') for item in data)
    
    # Count IPs
    ip_counts = Counter(item.get('ip', 'unknown') for item in data)
    
    # Count domains by TLD
    tld_counts = Counter(item.get('domainname', '').split('.')[-1] for item in data)
    
    # Count domains by date
    date_counts = Counter(item.get('firstseen', '') for item in data)
    
    # Get top IPs
    top_ips = dict(ip_counts.most_common(10))
    
    # Get top TLDs with the specified limit
    top_tlds = dict(tld_counts.most_common(tld_limit))
    
    return {
        'total_domains': len(data),
        'type_counts': dict(type_counts),
        'top_ips': top_ips,
        'top_tlds': top_tlds,
        'date_counts': dict(date_counts)
    }

def search_data(data, query):
    if not query:
        return data
    query = query.lower()
    return [item for item in data if 
            query in item.get('domainname', '').lower() or
            query in item.get('ip', '').lower() or
            query in str(item.get('type', '')).lower()]

def paginate_data(data, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return data[start:end]

def get_pagination_range(current_page, total_pages, window=5):
    """Get a range of page numbers to display, centered around current page"""
    if total_pages <= window:
        return range(1, total_pages + 1)
    
    half_window = window // 2
    start = max(1, current_page - half_window)
    end = min(total_pages, start + window - 1)
    
    if end - start + 1 < window:
        start = max(1, end - window + 1)
    
    return range(start, end + 1)

def get_tld_data():
    try:
        # Common legitimate TLDs to exclude
        blacklisted_tlds = {
            'com', 'net', 'org', 'nl'
        }
        
        url = "https://isc.sans.edu/api/recentdomains?json"
        print(f"[INFO] Making request to: {url}")
        
        print("[INFO] Waiting 15 seconds before making request...")
        time.sleep(15)
        
        max_retries = 3
        retry_count = 0
        
        headers = {
            'User-Agent': 'StormInt',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        while retry_count < max_retries:
            start_time = time.time()
            response = requests.get(url, headers=headers)
            elapsed_time = time.time() - start_time
            
            print(f"[DEBUG] Status code: {response.status_code}")
            print(f"[DEBUG] Headers: {dict(response.headers)}")
            print(f"[DEBUG] Request duration: {elapsed_time:.2f} seconds")
            
            try:
                if elapsed_time < 10:
                    wait_time = 10 - elapsed_time
                    print(f"[INFO] Waiting extra {wait_time:.2f} seconds to avoid rate limiting...")
                    time.sleep(wait_time)
                
                data = response.json()
                if data:
                    print("[INFO] Successfully parsed JSON response.")
                    break
                else:
                    print("[WARN] Empty JSON response.")
            except json.JSONDecodeError:
                print(f"[ERROR] Failed to parse JSON (attempt {retry_count + 1}/{max_retries})")
                print(f"[DEBUG] Response preview: {response.text[:200]}...")
                print("[INFO] Retrying after 20 seconds...")
                time.sleep(20)
                retry_count += 1
                continue
        
        if retry_count == max_retries:
            print("[FATAL] Max retries reached. Exiting.")
            return None
            
        # Extract and count TLDs, excluding blacklisted ones
        tlds = [
            domain["domainname"].rsplit(".", 1)[-1]
            for domain in data if domain.get("domainname") and "." in domain["domainname"]
            and domain["domainname"].rsplit(".", 1)[-1] not in blacklisted_tlds
        ]
        tld_counts = Counter(tlds)
        top_tlds = [{"tld": tld, "count": count} for tld, count in tld_counts.most_common(50)]
        
        return top_tlds
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    port_limit = request.args.get('port_limit', 100, type=int)
    tld_limit = request.args.get('tld_limit', 50, type=int)
    data = fetch_sans_data()
    top_ips = fetch_top_ips()
    top_ports = fetch_top_ports(port_limit)
    stats = analyze_data(data, tld_limit)
    
    # Paginate the raw data
    total_items = len(data)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    paginated_data = paginate_data(data, page, ITEMS_PER_PAGE)
    pagination_range = get_pagination_range(page, total_pages)
    
    return render_template('index.html', 
                         stats=stats,
                         raw_data=paginated_data,
                         top_ips=top_ips,
                         top_ports=top_ports,
                         current_page=page,
                         total_pages=total_pages,
                         total_items=total_items,
                         pagination_range=pagination_range,
                         port_limit=port_limit,
                         tld_limit=tld_limit)

@app.route('/api/stats')
def api_stats():
    data = fetch_sans_data()
    stats = analyze_data(data)
    return jsonify(stats)

@app.route('/search')
def search():
    # Get all filter parameters
    query = request.args.get('q', '').lower()
    domain_filter = request.args.get('domain', '').lower()
    ip_filter = request.args.get('ip', '').lower()
    type_filter = request.args.get('type', '').lower()
    firstseen_filter = request.args.get('firstseen', '').lower()
    page = request.args.get('page', 1, type=int)
    port_limit = request.args.get('port_limit', 100, type=int)
    tld_limit = request.args.get('tld_limit', 50, type=int)
    
    # Get all data
    data = fetch_sans_data()
    
    # Filter data based on search criteria
    filtered_data = []
    for item in data:
        # Safely handle None values
        domain = item.get('domainname', '').lower() if item.get('domainname') else ''
        ip = item.get('ip', '').lower() if item.get('ip') else ''
        type_val = item.get('type', '').lower() if item.get('type') else ''
        first_seen = item.get('firstseen', '').lower() if item.get('firstseen') else ''
        
        # Check if item matches all filters
        matches = True
        
        # Check general search query
        if query and not (query in domain or query in ip or query in type_val or query in first_seen):
            matches = False
        
        # Check individual column filters
        if domain_filter and domain_filter not in domain:
            matches = False
        if ip_filter and ip_filter not in ip:
            matches = False
        if type_filter and type_filter not in type_val:
            matches = False
        if firstseen_filter and firstseen_filter not in first_seen:
            matches = False
            
        if matches:
            filtered_data.append(item)
    
    # Calculate pagination
    total_items = len(filtered_data)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    paginated_data = filtered_data[start_idx:end_idx]
    
    # Get pagination range
    pagination_range = get_pagination_range(page, total_pages)
    
    # Get top IPs
    top_ips = fetch_top_ips()
    
    # Get top ports
    top_ports = fetch_top_ports(port_limit)
    
    # Analyze data for statistics
    stats = analyze_data(filtered_data, tld_limit)
    
    # Create template arguments
    template_args = {
        'stats': stats,
        'raw_data': paginated_data,
        'top_ips': top_ips,
        'top_ports': top_ports,
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'pagination_range': pagination_range,
        'port_limit': port_limit,
        'tld_limit': tld_limit
    }
    
    # Add search parameters to template args
    if query:
        template_args['q'] = query
    if domain_filter:
        template_args['domain'] = domain_filter
    if ip_filter:
        template_args['ip'] = ip_filter
    if type_filter:
        template_args['type'] = type_filter
    if firstseen_filter:
        template_args['firstseen'] = firstseen_filter
    
    return render_template('index.html', **template_args)

@app.route('/api/tlds')
def get_tlds():
    tld_data = get_tld_data()
    if tld_data:
        return jsonify(tld_data)
    else:
        return jsonify({"error": "Failed to fetch TLD data"}), 500

if __name__ == '__main__':
    app.run(debug=True) 