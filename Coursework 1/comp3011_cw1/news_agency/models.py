from django.db import models

# Create your models here.
class Story(models.Model):
    headline = models.CharField(max_length=64)
    CATEGORY_OPTIONS = {"pol":"Politics",
               "art":"Art",
               "tech":"Technology",
               "trivia":"Trivia"}
    
    category = models.CharField(max_length=32, choices=CATEGORY_OPTIONS)  #Category field must be one of the 4 choices. max_length has just been selected arbitrarily

    REGION_OPTIONS = {
        "uk": "United Kingdom",
        "eu": "Europe",
        "w": "World"
    }

    region = models.CharField(max_length=32, choices=REGION_OPTIONS)

    author = models.CharField(max_length=64)
    date =  models.DateTimeField("story date")
    details = models.CharField(max_length=128)

    def __str__(self): #added to make reading the database more human friendly
        return self.headline #this outputs headline to djhango terminal when doing Story.objects.all()


class Author(models.Model):
    name = models.CharField(max_length=64)
    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self): #added to make reading the database more human friendly
        return self.username #this outputs headline to djhango terminal when doing Story.objects.all()

