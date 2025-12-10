from django.contrib import admin
from .models import Movie, Watchlist

# Register your models here.
admin.site.register(Movie)
admin.site.register(Watchlist)