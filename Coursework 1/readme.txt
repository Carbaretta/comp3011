##########################
Client Usage:
##########################
Run the client with "python client.py". You will receive a prompt "Enter command" with a list of following commands.
These have been implemented exactly as the spec suggests. For example inputting the following:

news -id="JES03" -cat="art"

will fetch all art stories for the agency with code "JES03". A list of all commands is seen below:
--------------------------
login <url>
Where url is a domain you wish to login to. If providing a protocol, you must check if it is http:// or https://, as some services are sensitive to this. If a protocol is missing from the inputted URL, it will automatically append "http://". Trailing slashes are also automatically appended.

delete and post commands cannot be used unless you are logged in. You can only login to one service at a time.
--------------------------
logout
This will log you out of the service you are currently logged into. You must log back into a service in order to run delete or post commands.
--------------------------
post
You must be logged in to use this command. The post will be published to the service you are logged into.
You will be prompting for a headline, category, region and details of your story. These must meet the following requirements:

headline must be 64 characters or less
category must be one of "art", "tech", "pol" or "trivia
--------------------------
news [-id=] [-cat=] [-reg=] [-date=]
Where id, cat, reg and date are all optional switches. the "=" and quotes are not necessary; i.e. doing "news -id='JES03'" and doing "news -id JES03" are equivalent.

-id is the id of the news service you wish to request stories from.
-cat is the category of news you wish you read, this can be one of "art", "tech", "pol" and "trivia".
-reg is the region you want to read about. This can be one of "uk", "eu" or "w"
-data is the date at or after which a story has happened. this should be in dd/mm/yyyy format.
--------------------------
list
This command lists all news services in the directory.
--------------------------
delete story_key
This command will delete a story with the given key .You must be logged in to use this command.
--------------------------
exit
This will terminate the client.
--------------------------

##########################
Pythonanywhere domain
##########################

PythonAnywhere domain for the API server is http://ed20jes.pythonanywhere.com. You MUST use http://, not https:// to login. https:// is not supported, as this was never specified in the coursework spec.

##########################
Module leaders account details:
##########################
Username: ammar
password: COMP3011Pass

Details are same for both the admin and author login.

Other information: