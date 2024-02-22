import requests
import json



#create new sessions to allow persistence 
session = requests.Session()

# Specify the URL
url = "http://127.0.0.1:8000/api/"


print("Testing initial auth")
response = requests.post(url + 'otherAction/')
print(response.text)


print("Testing logout without loggin in")
response = requests.post(url + 'logout/')
print(response)

# Define the JSON payload
json_payload = {"username": "jacob", "password": "adminpassword"}

# Convert the payload to JSON format

# Set the headers
headers = {"Content-Type": "application/x-www-form-urlencoded"}

# Make the POST request
print("Logging in")
response = session.post(url + 'login/', data=json_payload, headers=headers)

# Check the response
if response.status_code == 200:

    print("Response:", response.text)
else:
    print("POST request failed. Status code:", response.status_code)
    print("Response:", response.text)

print("Testing auth after login")
response = session.post(url + 'otherAction/' , headers=headers)
print(response.text)


headers_story = {"Content-Type": "application/json"}
print("Creating story")
story_payload = {"headline": "A new valid headline.", "category": "art", "details":"Some made up story", "region":"uk"}
response = session.post(url + 'story/' , json=story_payload, headers=headers_story)
print(response)


print("Logging out")
response = session.post(url + 'logout/')
print(response.text)

print("testing auth after logout")
response = session.post(url + 'otherAction/' , headers=headers)
print(response.text)

