from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.core.serializers import serialize

from urllib.parse import urlparse, parse_qs

from .models import Story, Author
import json
import datetime
import re

def index(request):
    return HttpResponse("This is the page for the API.")


'''
Turned off CSRF token usage for sake of saving time. Whilst not good in practice, makes doing the login process significantly less complex.

Commented out implementation below defaults to using the in-built user table that also holds data about Superusers. I wanted to keep these separated as per spec.
'''

""" @csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            request.session.save()
            return HttpResponse(status=200, content=f"Successfully logged in. Welcome.", content_type='text/plain')
        else:
            return HttpResponse(status=401, content=f"Username or password invalid", content_type='text/plain')
    else:
        return HttpResponse("Form input required")
 """

###Custom implementation of password/user checking
@csrf_exempt
def userLogin(request):
    if request.method == "POST": #data should be received as POST payload
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username != None and password != None:
            try:
                author_user = Author.objects.get(username=username)
            except Exception as e:
                return HttpResponse(status=401, content=f"Username or password invalid", content_type='text/plain')

            if author_user != None:
                print("User found:", author_user.password)
                if author_user.password == password:
                    request.session['username'] = username
                    request.session['name'] = author_user.name
                    request.session.save()
                    return HttpResponse(status=200, content=f"Successfully logged in. Welcome.", content_type='text/plain')
                else:
                    return HttpResponse(status=401, content=f"Username or password invalid", content_type='text/plain')
            else:
                return HttpResponse(status=401, content=f"Username or password invalid", content_type='text/plain')
        else:
            return HttpResponse(status=401, content=f"Username or password not provided", content_type='text/plain')
    else:
        return HttpResponse(status=400, content=f"Request must be POST", content_type='text/plain')

@csrf_exempt
def userLogout(request):
    if request.session.get("username"):
        logout(request)
        # clear the user's session data
        Session.objects.filter(session_key=request.session.session_key).delete()
        return HttpResponse(status=200, content=f"Successfully logged out. Goodbye.", content_type='text/plain')
    else:
        return HttpResponse(status=401, content=f"You are not logged in. Unable to log out.", content_type='text/plain')


@csrf_exempt
def manageStories(request): #handles all requests to /api/stories/
    if request.method == "POST":    #if post, its for creating a new story
        response =  createStory(request)
        return response
    elif request.method == "GET":   #if get, its for fetching stories
        response = getStories(request)
        return response

    
@csrf_exempt
def getStories(request):    #fetch all stories, filtered against user specified filters
    query_params = parse_qs(request.META["QUERY_STRING"])

    if len(query_params) != 3:
        return HttpResponse(status=404, content="Bad query parameters given", content_type="text/plain")
    print("Query params:", query_params)
    filter_conditions = {}  #build a filter list
    
    if query_params["story_cat"][0] != "*":
        if (not query_params["story_cat"][0] in ("art", "pol", "tech", "trivia")):
            return HttpResponse(status=404, content=f"Bad category given. Must be 'art', 'pol', 'tech' or 'trivia'", content_type='text/plain')
        filter_conditions["category"] = query_params["story_cat"][0]
    if query_params["story_region"][0] != "*":
        if (not query_params["story_region"][0] in ("w","uk","eu")):
            return HttpResponse(status=404, content=f"Bad region given. Must be 'w', 'uk', 'eu' ", content_type='text/plain')
        filter_conditions["region"] = query_params["story_region"][0]
    if query_params["story_date"][0] != "*":
        date_filter = datetime.datetime.strptime(query_params["story_date"], "%d/%m/%y") ##extract text format into actual datetime object 
        filter_conditions["date__gte"] = date_filter.strftime("%Y-%m-%d 00:00:00.000000") ##create filter. __gte append makes the filter such we filter dates "greater than or equal"


    print("Conditions:", filter_conditions)
    try:
        filtered_stories = Story.objects.filter(**filter_conditions)    #enter filter conditions with kwargs
        if len(filtered_stories) == 0:
            return HttpResponse(status=404, content=f"No stories found for search criteria.", content_type='text/plain')
    except:
        return HttpResponse(status=404, content=f"Invalid search criteria.", content_type='text/plain')
    
    
    serialised_filtered_stories = json.loads(serialize('json', filtered_stories)) #serialise function converts from object to string representation.
                                                                                #json.loads then converts from string to indexable dictionary
    
    story_array = []
    
    for story in serialised_filtered_stories: #grab the details from the serialised QuerySet and convert to correct data structure
        individual_story = {}
        print("Story is:", story)
        individual_story["key"] = story["pk"]
        individual_story["headline"] = story["fields"]["headline"]
        individual_story["story_cat"] = story["fields"]["category"]
        individual_story["story_region"] = story["fields"]["region"]
        individual_story["author"] = story["fields"]["author"]
        individual_story["story_date"] = story["fields"]["date"]
        individual_story["story_details"] = story["fields"]["details"]

        story_array.append(individual_story)

    stories_json = {"stories": story_array} #place into finalised format
    return HttpResponse(status = 200, content=json.dumps(stories_json), content_type="application/json")


@csrf_exempt
def createStory(request):
    if request.session.get("username"): #check user is logged in
        json_payload = json.loads(request.body.decode('utf-8'))
        print(json_payload)
        headline = json_payload['headline']
        category = json_payload['category']
        region = json_payload['region']
        details = json_payload['details']
        valid_flag = True
        validation_array = []
        
        if (len(headline) > 64): #validation for the story data. Appends all invalidating reasons to an array
            valid_flag = False
            validation_array.append("Headline too long. Must be 64 chars or less. ")
        if (not (region in ("w","uk","eu"))):
            valid_flag = False
            validation_array.append("Invalid region given. Must be 'w', 'uk' or 'eu'. ")
        if (len(details) > 128):
            valid_flag = False
            validation_array.append("Details too long. Must be 128 characters or less. ")
        if (not(category in ("art", "pol", "tech", "trivia"))):       
            validFlag = False
            validation_array.append("Invalid category given. Must be 'art', 'pol', 'tech' or 'trivia'. ")

        if valid_flag:    
            Story.objects.create(headline=headline, category=category, region=region, details=details, author=request.session["name"], date=datetime.datetime.now())
            return HttpResponse(status=201)
        else:
            response = HttpResponse(status = 503, content=''.join(validation_array), content_type="text/plain") #builds the invalid reason message and sends to client
            response.__setattr__("status_code", 503)
            return response

    else:
        response = HttpResponse("You are not authenticated.")
        response.__setattr__("status_code", 503)
        return response

@csrf_exempt
def deleteStory(request, key):
    if request.session.get("username"): #if theyre logged in
        if len(Story.objects.filter(id=key)) == 1: #checking theres a corresponding ID
            try:
                Story.objects.filter(id=key).delete()
                return HttpResponse(status=200)  # Successful deletion, respond with 200 OK
            except Exception as e:
                return HttpResponse(status=503, content=f"Failed to delete story.", content_type='text/plain')
        else:
            return HttpResponse(status=503, content=f"Story not found", content_type='text/plain')
    return HttpResponse(status=401, content=f"You are not authenticated.", content_type='text/plain')