import requests

response = requests.get(url="http://127.0.0.1/api/stories?story_region=*&story_cat=*&story_date=*")

print(response.text)