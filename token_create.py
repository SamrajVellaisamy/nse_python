import json
import requests 

class Token():
    # Base URL to initialize Akamai cookies, and the target API endpoint
    home_url = "https://www.nseindia.com/"
    api_url = "https://www.nseindia.com/api/NextApi/cmsHandler?functionName=getNotificationList"

    # Exact browser headers required to bypass the security wall
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
    }
 

    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.nseindia.com/"

        self.session.headers.update(
            {
                "User-Agent": self.headers["User-Agent"],
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com",
                "Connection": "keep-alive",
            }
        )

        self.initialize_session()

    def initialize_session(self):
        try:
            print("Initializing NSE Session...")

            response = self.session.get(
                self.base_url,
                timeout=15 
            )

            # Step 1: Hit the home page to collect base cookies (nsit, ak_bmsc, _abck, etc.)
            print("Initializing session on NSE homepage...")
            self.session.get(self.home_url, timeout=15)
            
            # Step 2: Hit the specific CMS Handler API endpoint using the active session
            print("Fetching target API endpoint...")
            response = self.session.get(self.api_url, timeout=15)
            
            # Step 3: Extract the combined cookies from the session into a flat dictionary
            cookie_dict = self.session.cookies.get_dict()
            
            # Step 4: Write cookies directly to your JSON file
            file_name = "cookies"
            with open(file_name, "w", encoding="utf-8") as json_file:
                json.dump(cookie_dict, json_file, indent=4)
                
            print(f"\n[SUCCESS] Saved {len(cookie_dict)} cookies to {file_name}!") 

        except Exception as e:
            print(f"\n[ERROR] Connection failed: {e}")


tk = Token()