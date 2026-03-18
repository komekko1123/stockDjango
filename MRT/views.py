from django.shortcuts import render, get_object_or_404
from .models import Line, Direction, Station, Train, Timetable

# Create your views here.
def show_line(request):
    lines = Line.objects.all()
    return render(request, 'MRT/show_line.html', {'lines': lines})

def show_direction(request, line_name):
    line = get_object_or_404(Line, line_name=line_name)
    directions = line.directions.all()
    return render(request, 'MRT/show_direction.html', {'line': line, 'directions': directions})

def show_station(request, line_name, direction_name):
    line = get_object_or_404(Line, line_name=line_name)
    direction = get_object_or_404(Direction, direction_name=direction_name)
    stations = line.stations.all()
    return render(request, 'MRT/show_station.html', {'line': line, 'direction': direction, 'stations': stations})

def show_train_time(request, line_name, direction_name, station_name, day_type):
    line = get_object_or_404(Line, line_name=line_name)
    direction = get_object_or_404(Direction, direction_name=direction_name)
    station = get_object_or_404(Station, station_name=station_name)
    trains = direction.trains.filter(day_type=day_type)
    timetables = Timetable.objects.filter(
        train_number__in=trains,  # 火車號在篩選出的火車列表中
        station_name=station      # 車站名稱匹配
    )
    return render(request, 'MRT/show_train_time.html', {'line': line, 'direction': direction, 'station': station, 'trains': trains, 'day_type': day_type, 'timetables': timetables})

def show_train(request, direction_name, day_type, train_number):
    direction = get_object_or_404(Direction, direction_name=direction_name)
    train = get_object_or_404(
        Train,
        direction_name=direction,  # 傳入 Direction 對象
        day_type=day_type,
        train_number=train_number
    )
    timetables = train.timetables.all()
    return render(request, 'MRT/show_train.html', {'direction_name': direction_name, 'day_type': day_type, 'train_number': train_number, 'timetables': timetables})

def show_MRT_hall(request):
    return render(request, 'MRT/show_MRT_hall.html')
