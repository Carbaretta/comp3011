from django.contrib import admin


from .models import Story, Author
# Register your models here.

admin.site.register(Story)
admin.site.register(Author)
