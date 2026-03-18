from django.contrib import admin

from .models import Line, Direction, Station, Train, Timetable

# Register your models here.
admin.site.register(Line)
admin.site.register(Direction)
admin.site.register(Station)
admin.site.register(Train)
admin.site.register(Timetable)