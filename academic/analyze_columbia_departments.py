import requests
from bs4 import BeautifulSoup

def analyze_columbia_departments():
    departments = [
        ('Classics', 'https://classics.columbia.edu/events'),
        ('Mathematics', 'https://math.columbia.edu/events'),
        ('Law', 'https://law.columbia.edu/events'),
        ('History', 'https://history.columbia.edu/events')
    ]
    
    print("COLUMBIA DEPARTMENT EVENT QUALITY ANALYSIS")
    print("=" * 60)
    
    for dept_name, url in departments:
        print(f"\n{dept_name.upper()} DEPARTMENT:")
        print("-" * 40)
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find event-related content
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            event_headers = [h.get_text().strip() for h in headers if h.get_text().strip()]
            
            # Look for academic event indicators
            content = soup.get_text().lower()
            academic_indicators = {
                'lecture': content.count('lecture'),
                'seminar': content.count('seminar'),
                'conference': content.count('conference'),
                'colloquium': content.count('colloquium'),
                'symposium': content.count('symposium'),
                'workshop': content.count('workshop')
            }
            
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)} characters")
            print(f"Academic event indicators: {academic_indicators}")
            
            print("Event headers found:")
            for i, header in enumerate(event_headers[:10]):
                print(f"  {i+1}. {header}")
            
            if len(event_headers) > 10:
                print(f"  ... and {len(event_headers) - 10} more")
            
            # Quality assessment
            academic_count = sum(academic_indicators.values())
            if academic_count > 10:
                quality = "⭐⭐⭐⭐⭐ EXCELLENT"
            elif academic_count > 5:
                quality = "⭐⭐⭐⭐ HIGH"
            elif academic_count > 2:
                quality = "⭐⭐⭐ GOOD"
            else:
                quality = "⭐⭐ FAIR"
            
            print(f"Quality Assessment: {quality}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    analyze_columbia_departments()
