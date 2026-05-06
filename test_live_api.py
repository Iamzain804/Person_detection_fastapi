import requests

url = "https://muhammadzain09-ai-person-detector-api.hf.space/api/v1/detect"
headers = {"X-API-Key": "your-super-secret-api-key"}

# Using a public image for testing
image_url = "https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/assets/bus.jpg"
image_data = requests.get(image_url).content

files = {'file': ('test.jpg', image_data, 'image/jpeg')}

print(f"Connecting to: {url}...")
try:
    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        print("Success! API is responding correctly.")
        print("Detection Results:", response.json())
    else:
        print(f"Failed with status code: {response.status_code}")
        print("Response:", response.text)
except Exception as e:
    print(f"Error connecting to API: {str(e)}")
