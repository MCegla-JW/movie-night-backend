from django.contrib import admin
from .models import Party, PartyMovie, Vote

# Register your models here.
admin.site.register(Party)
admin.site.register(PartyMovie)
admin.site.register(Vote)