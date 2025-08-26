import requests
from datetime import datetime, timedelta

def debug_juilliard_api():
    """Debug the Juilliard API to see what's happening"""
    
    # Get current date and next month
    current_date = datetime.now()
    next_month = current_date + timedelta(days=30)
    
    # Format dates for the API
    start_date = current_date.strftime("%Y-%m-%d")
    end_date = next_month.strftime("%Y-%m-%d")
    
    url = "https://www.juilliard.edu/views/ajax"
    
    querystring = {
        "view_name": "event_performance_calendar",
        "view_display_id": "block_1",
        "view_args": "",
        "view_path": "node/1",
        "view_base_path": "event-performance-calendar",
        "view_dom_id": "1",
        "pager_element": "0",
        "page": "0",
        "field_event_date_value": f"{start_date} to {end_date}",
        "_wrapper_format": "drupal_ajax"
    }
    
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.juilliard.edu/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    
    print(f"Making request to: {url}")
    print(f"Query parameters: {querystring}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON response type: {type(json_data)}")
                print(f"JSON response length: {len(json_data) if isinstance(json_data, list) else 'not a list'}")
                if isinstance(json_data, list) and json_data:
                    print(f"First item: {json_data[0]}")
            except Exception as e:
                print(f"JSON parsing error: {e}")
        else:
            print(f"Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_juilliard_api()
