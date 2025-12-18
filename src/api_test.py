import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_tfl_api():
    key = os.getenv("TFL_APP_KEY")
    # Let's check the live status of the Victoria Line
    url = f"https://api.tfl.gov.uk/Line/victoria/Status?app_key={key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        status = data[0]['lineStatuses'][0]['statusSeverityDescription']
        print(f"✅ API SUCCESS! Line: Victoria - Status: {status}")
    else:
        print(f"❌ API FAILED. Check your key. Error: {response.status_code}")

if __name__ == "__main__":
    test_tfl_api()