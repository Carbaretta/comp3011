import argparse
import requests
import json
from itertools import islice
from datetime import datetime

class Client:
    def __init__(self):
        self.sessionData = {"login_url": "", "logged_in": False, "agencies": []}
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

        # EXIT command
        subparsers.add_parser("exit", help="Exit program")

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
            command_input = input("Enter command (login, logout, post, news, list, delete, exit): ")
            args =None
            try:
                args = parser.parse_args(command_input.split())
            except:
                continue
            
            if(args):
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
                elif args.command == "exit":
                    exit(0)
                else:
                    print("Unknown command")

            


    def login(self, args):
        if args.url[-1] == "/": #check if the path is fully qualified on the url
            self.sessionData["login_url"] = args.url
        else:
            self.sessionData["login_url"] = args.url + "/"

        if (not "https://" in self.sessionData["login_url"]) and not ("http://" in self.sessionData["login_url"]):
            self.sessionData["login_url"] = "http://" + self.sessionData["login_url"] #default to http://

        username = input("What is your username?: ")
        password = input("What is your password?: ")

        json_payload = {"username": username, "password": password}

        # Set the headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Make the POST request
        print("Logging in")
        
        try:
            response = self.session.post(self.sessionData["login_url"] + 'api/login', data=json_payload, headers=headers)
            if int(response.status_code) == 200:
                self.sessionData["logged_in"] = True
            print(response.text)
        except Exception as e:
            print("Log in attempt failed. Reason: ", e)

        
        

    def logout(self, args):
        # Implement logout logic here
        if self.sessionData["logged_in"]:
            try:
                response = self.session.post(self.sessionData["login_url"] + 'api/logout')
            except Exception as e:
                print("Logout failed: ", e)

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
            if len(headline) > 64 or len(headline) < 1:
                print("Invalid headline given. Must be between 1 and 64 characters")
                return
            category = input("What is the story category?: ")
            category = category.replace(" ", '') #strip whitespace
            if category not in ("pol", "art", "tech", "trivia"):
                print("Invalid category given. Must be one of  'art', 'tech', 'pol', 'trivia'")
                return
            
            details = input("What are the details of the story?: ")
            if len(details) > 128 or len(details) < 1:
                print("Invalid details given. Must be between 1 and 128 characters")
                return
            
            region = input("Which region is the story for?: ")
            region = region.replace(" ", '')
            if region not in ("uk", "w", "eu"):
                print("Invalid category given. Must be one of  'art', 'tech', 'pol', 'trivia'")
                return
            
            story_payload = {"headline": headline, "category": category, "details":details, "region":region}
            response = self.session.post(self.sessionData["login_url"] + 'api/stories' , json=story_payload, headers=headers_story)
            if (response.status_code == 201):
                print("Story successfully created")
            else:
                print(response.content.decode("utf-8"))
        else:
            print("You are not logged in.")
        
    def validDate(self, date):
        try:
            datetime.strptime(date, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def news(self, args):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        story_json = {"story_cat": "*","story_region":"*" ,"story_date":"*" }
        if args.cat:
            story_json["story_cat"] = args.cat.replace('"', '')
            if story_json["story_cat"] not in ("pol", "art", "tech", "trivia"):
                print("Invalid category given. Must be one of  'art', 'tech', 'pol', 'trivia'")
                return

        if args.reg:
            story_json["story_region"] = args.reg.replace('"', '')
            if story_json["story_region"] not in ("uk", "w", "eu"):
                print("Invalid region given. Must be one of  'uk', 'w', 'eu'")
                return

        if args.date:
            story_json["story_date"] = args.date.replace('"', '')
            if not self.validDate(story_json["story_date"]):
                print("Invalid date given. Must be in format dd/mm/yyyy")
                return

        if args.id:
            args.id = args.id.replace('"', '')

        if not(self.sessionData["agencies"]):
            self.get_services()
 
        query_string = '&'.join([f'{key}={value}' for key, value in story_json.items()])

        storiesPrinted = 0

        if args.id: #only do if specific agency
            agencyFound = False
            for agency in self.sessionData["agencies"]:
                if agency["agency_code"] == args.id:
                    agencyFound = True
                    response = None
                    try:
                        response = self.session.get(agency["url"] + '/api/stories?' + query_string, headers=headers)
                    except Exception as e:
                        print("Failed to fetch news from agency.")

                    if response:
                        if response.status_code == 200:
                            if response.text:
                                print("==========" + agency["agency_name"] + "=========")
                                self.display_news(response.text, storiesPrinted)
                        else:
                            print("Failed to fetch news from ", agency["agency_name"])
                else:
                    pass
            if not agencyFound:
                print("Agency not found.")
        else:
            for agency in self.sessionData["agencies"]:
                if storiesPrinted < 20:
                    try:
                        response = self.session.get(agency["url"] + '/api/stories?' + query_string, headers=headers)
                        if response.status_code == 200:
                            if len(response.text) > 0:
                                print("==========" + agency["agency_name"] + "=========")
                                storiesPrinted = self.display_news(response.text, storiesPrinted)
                            else:
                                print("Failed to fetch news from ", agency["agency_name"])
                            
                    except Exception as e:
                        print("Failed to get ", agency["url"])
                else:
                    break


    def display_news(self, text, storiesPrinted):

        stories = json.loads(text)
        try:
            for story in stories["stories"]:
                if storiesPrinted < 20:
                    print("-----------------------------------------------")
                    print(story["headline"])
                    print("Published on " + str(story["story_date"]) + " | " + story["story_region"] + " | " + story["story_cat"] + " | Written by " + story["author"] + " | Story ID: " + str(story["key"]))
                    print(story["story_details"])
                    print("-----------------------------------------------")
                    storiesPrinted += 1
                else:
                    return storiesPrinted #limited exceeded, return
            
            return storiesPrinted #limit not yet exceeded
        except Exception as e:
            print("Failed to decode JSON", e)
            return storiesPrinted

    def delete(self, args):
        if self.sessionData["logged_in"]:
            response = self.session.delete(self.sessionData["login_url"] + 'api/stories/' + args.story_key)
            if response.status_code == 200:
                print("Story deleted successfully")
            else:
                print("error: ", response.content.decode('utf-8'))
        else:
            print("You are not logged in.")

    def get_services(self):
        try:
            response = self.session.get("http://newssites.pythonanywhere.com/api/directory")
            self.sessionData["agencies"] = json.loads(response.text)
        except Exception as e:
            return e

    def list_services(self, args):
        try:
            if not(self.sessionData["agencies"]):
                self.get_services()
            for agency in islice(self.sessionData["agencies"], 100):
                print(agency["agency_code"]+ ": ", agency["agency_name"])
        except Exception as e:
            print("Fetch agencies failed with error: ", e)
        



if __name__ == "__main__":
    client = Client()
