import requests

# API Configuration
URL = "http://127.0.0.1:8000/api/v1/detect"
API_KEY = "your-super-secret-api-key" # Jo aapne .env mein rakha hai
IMAGE_PATH = "test_image.jpg" # Kisi bhi image ka path

def test_detection():
    # Headers mein API Key bhejein
    headers = {"X-API-Key": API_KEY}
    
    # Image file ko open karein
    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"file": f}
            
            print(f"Sending request to {URL}...")
            response = requests.post(URL, headers=headers, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("\n--- Detection Results ---")
                print(f"Persons Found: {data['count']}")
                for i, det in enumerate(data['detections']):
                    print(f"Person {i+1}: Confidence {det['confidence']:.2f}, Box: {det['box']}")
                print(f"Inference Time: {data['inference_time']:.4f}s")
                print("-------------------------")
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                
    except FileNotFoundError:
        print(f"Error: Image file '{IMAGE_PATH}' nahi mili. Pehle koi image is folder mein rakhein.")

if __name__ == "__main__":
    test_detection()
