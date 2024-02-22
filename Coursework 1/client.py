import argparse
import requests
import json

class Client:
    def __init__(self):
        self.sessionData = {"url": "", "logged_in": False}
        self.session = requests.Session()
        self.main()
        
        

    def main(self):
        parser = argparse.ArgumentParser(description="News Service Command Line Tool")

        subparsers = parser.add_subparsers(title="Commands", dest="command")

        # LOGIN command
        login_parser = subparsers.add_parser("login", help="Login to a news service")
        login_parser.add_argument("url", help="Address of the service")

        # LOGOUT command
        subparsers.add_parser("logout", help="Logout from the current session")

        # POST command
        subparsers.add_parser("post", help="Post a news story")

        # NEWS command
        news_parser = subparsers.add_parser("news", help="Request news stories from a web service")
        news_parser.add_argument("-id", help="ID of the news service")
        news_parser.add_argument("-cat", help="News category")
        news_parser.add_argument("-reg", help="Region of the required stories")
        news_parser.add_argument("-date", help="Date at or after which a story has happened")

        # LIST command
        subparsers.add_parser("list", help="List all news services in the directory")

        # DELETE command
        delete_parser = subparsers.add_parser("delete", help="Delete a news story")
        delete_parser.add_argument("story_key", help="Key of the news story to delete")
        while True:
            command_input = input("Enter command: ")

            if not command_input:
                break
            args = parser.parse_args(command_input.split())

            if args.command == "login":
                self.login(args)
            elif args.command == "logout":
                self.logout(args)
            elif args.command == "post":
                self.post(args)
            elif args.command == "news":
                self.news(args)
            elif args.command == "list":
                self.list_services(args)
            elif args.command == "delete":
                self.delete(args)
            else:
                print("Unknown command")


    def login(self, args):
        if args.url[-1] == "/": #check if the path is fully qualified on the url
            self.sessionData["url"] = args.url
        else:
            self.sessionData["url"] = args.url + "/"
            print(self.sessionData["url"])

        # Implement login logic here
        username = input("What is your username?: ")
        password = input("What is your password?: ")

        json_payload = {"username": username, "password": password}

        # Set the headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Make the POST request
        print("Logging in")
        response = self.session.post(self.sessionData["url"] + 'api/login/', data=json_payload, headers=headers)

        if int(response.status_code) == 200:
            self.sessionData["logged_in"] = True
        
        print(response.text)
        

    def logout(self, args):
        # Implement logout logic here
        if self.sessionData["logged_in"]:
            response = self.session.post(self.sessionData["url"] + 'api/logout/')
            if int(response.status_code) == 200:
                self.sessionData["logged_in"] == False
            print(response.text)
        else:
            print("No logged in session to logout of!")

        

    def post(self, args):
        if self.sessionData["logged_in"]:
            headers_story = {"Content-Type": "application/json"}
            print("Creating story")
            
            headline = input("What is the story headline?: ")
            category = input("What is the story category?: ")
            details = input("What are the details of the story?: ")
            region = input("Which region is the story for?: ")
            story_payload = {"headline": headline, "category": category, "details":details, "region":region}
            response = self.session.post(self.sessionData["url"] + 'api/stories/' , json=story_payload, headers=headers_story)
            if (response.status_code == 201):
                print("Story successfully created")
            else:
                print(response.content.decode("utf-8"))
        else:
            print("You are not logged in.")
        


    def news(self, args):
        if self.sessionData["logged_in"]:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            story_json = {"story_cat": "*","story_region":"*" ,"story_date":"*" }
            
            if args.id: #implement later
                pass

            if args.cat:
                story_json["story_cat"] = args.cat

            if args.reg:
                story_json["story_region"] = args.reg

            if args.date:
                story_json["story_date"] = args.date


            response = self.session.get(self.sessionData["url"] + 'api/stories/' , json=story_json, headers=headers)
            if response.status_code == 200:
                self.display_news(response.text)
            else:
                print(response.content.decode("utf-8"))
        else:
            print("You are not logged in.")

    def display_news(self, text):
        stories = json.loads(text)
        for story in stories["stories"]:
            print(str(story["key"]) + ": " + story["headline"])

    def delete(self, args):
        response = self.session.delete(self.sessionData["url"] + 'api/stories/' + args.story_key)
        if response.status_code == 200:
            print("Story deleted successfully")
        else:
            print("error: ", response.content.decode('utf-8'))

    def list_services(self, args):
        # Implement list services logic here
        print("List command", args)



if __name__ == "__main__":
    client = Client()
