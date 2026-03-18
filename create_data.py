import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebStockPredict.settings')
django.setup()

from MRT.models import Line, Direction, Station, Train, Timetable

# 若不存在相同名稱則創建一個線路
def create_line_if_not_exists(line_name):
    if not Line.objects.filter(line_name = line_name).exists():
        Line.objects.create(line_name = line_name)
        print(f"新增成功：{line_name}")
    else:
        print(f"資料已存在：{line_name}")

# 若不存在相同方向則創建一個方向
def create_direction_if_not_exists(direction_name, line_name):
    # 獲取對應的 Line 物件
    try:
        line = Line.objects.get(line_name=line_name)
    except Line.DoesNotExist:
        print(f"錯誤：找不到名稱為 {line_name} 的捷運線")
    else:
        # 檢查是否已經存在相同的 direction_name 和 line_name
        if not Direction.objects.filter(direction_name=direction_name, line_name=line).exists():
            Direction.objects.create(direction_name=direction_name, line_name=line)
            print(f"新增成功：{direction_name} 在 {line_name}")
        else:
            print(f"資料已存在：{direction_name} 在 {line_name}")

create_line_if_not_exists("淡水信義線")
create_direction_if_not_exists("往淡水", "淡水信義線")
create_direction_if_not_exists("往象山", "淡水信義線")

create_line_if_not_exists("松山新店線")
create_direction_if_not_exists("往松山", "松山新店線")
create_direction_if_not_exists("往新店", "松山新店線")

create_line_if_not_exists("中和新蘆線")
create_direction_if_not_exists("往蘆洲迴龍", "中和新蘆線")
create_direction_if_not_exists("往南勢角", "中和新蘆線")

create_line_if_not_exists("板南線")
create_direction_if_not_exists("往頂埔", "板南線")
create_direction_if_not_exists("往南港展覽館", "板南線")

def create_station_if_not_exists(station_name, line_name):
    # 獲取對應的 Line 物件
    try:
        line = Line.objects.get(line_name=line_name)
    except Line.DoesNotExist:
        print(f"錯誤：找不到名稱為 {line_name} 的捷運線")
    else:
        # 檢查是否已經存在相同的 station_name 和 line_name
        if not Station.objects.filter(station_name=station_name, line_name=line).exists():
            Station.objects.create(station_name=station_name, line_name=line)
            print(f"新增成功：{station_name} 在 {line_name}")
        else:
            print(f"資料已存在：{station_name} 在 {line_name}")

def create_train_if_not_exists(train_number, direction_name, day_type):
    # 獲取對應的 Direction 物件
    try:
        direction = Direction.objects.get(direction_name=direction_name)
    except Direction.DoesNotExist:
        print(f"錯誤：找不到 {direction_name} 的方向")
    else:
        # 檢查是否已經存在相同的 train_number 和 direction_name
        if not Train.objects.filter(train_number=train_number, direction_name=direction, day_type=day_type).exists():
            Train.objects.create(train_number=train_number, direction_name=direction, day_type=day_type)
            print(f"新增成功：{day_type}{direction_name}第{train_number}班車")
        else:
            print(f"新增成功：{day_type}{direction_name}第{train_number}班車")

def create_timetable_if_not_exists(train_number, station_name, arrival_time, direction_name, day_type):
    # 獲取對應的 Train 物件
    try:
        direction = Direction.objects.get(direction_name=direction_name)
        train = Train.objects.get(train_number=train_number, direction_name=direction, day_type=day_type)
        station = Station.objects.get(station_name=station_name)
    except Train.DoesNotExist:
        print(f"錯誤：找不到名稱為 {train_number} 的車次")
    except Direction.DoesNotExist:
        print(f"錯誤：找不到名稱為 {train_number} 的方向")
    except Station.DoesNotExist:
        print(f"錯誤：找不到名稱為 {station_name} 的車站")
    else:
        # 檢查是否已經存在相同的 train_number 和 station_name
        if not Timetable.objects.filter(train_number=train, station_name=station).exists():
            Timetable.objects.create(train_number=train, station_name=station, arrival_time=arrival_time)
            print(f"新增成功：第{train_number}班車 {arrival_time} 抵達{station_name}")
        else:
            print(f"資料已存在：第{train_number}班車 {arrival_time} 抵達{station_name}")

def create_station_train_timetable_if_not_exists(filename, line_name, direction_name, day_type):
    with open('MRTtable/' + filename + '.csv', 'r', encoding='big5') as file:
        f = csv.reader(file)

        line = []
        for row in f:
            line.append(row)

        # 新增新的捷運站
        stations = line[0][1:len(line[0])]
        for station_name in stations:
            create_station_if_not_exists(station_name, line_name)

        # 新增車次及時刻表
        trains = line[1:len(line)]
        for train in trains:
            create_train_if_not_exists(train[0], direction_name, day_type)
            
            times = train[1:len(train)]
            for i in range(len(times)):
                time = times[i]
                if time != "" and time != " " and time != "\t" :
                    create_timetable_if_not_exists(train[0], stations[i], time, direction_name, day_type)
            

create_station_train_timetable_if_not_exists("中和新蘆線時刻表_南勢角方向_平日", "中和新蘆線", "往南勢角", "平日")
create_station_train_timetable_if_not_exists("中和新蘆線時刻表_南勢角方向_假日", "中和新蘆線", "往南勢角", "假日")
create_station_train_timetable_if_not_exists("中和新蘆線時刻表_蘆洲迴龍方向_平日", "中和新蘆線", "往蘆洲迴龍", "平日")
create_station_train_timetable_if_not_exists("中和新蘆線時刻表_蘆洲迴龍方向_假日", "中和新蘆線", "往蘆洲迴龍", "假日")

create_station_train_timetable_if_not_exists("松山新店線時刻表_松山方向_平日", "松山新店線", "往松山", "平日")
create_station_train_timetable_if_not_exists("松山新店線時刻表_松山方向_假日", "松山新店線", "往松山", "假日")
create_station_train_timetable_if_not_exists("松山新店線時刻表_新店方向_平日", "松山新店線", "往新店", "平日")
create_station_train_timetable_if_not_exists("松山新店線時刻表_新店方向_假日", "松山新店線", "往新店", "假日")

create_station_train_timetable_if_not_exists("板南線時刻表_南港方向_平日", "板南線", "往南港展覽館", "平日")
create_station_train_timetable_if_not_exists("板南線時刻表_南港方向_假日", "板南線", "往南港展覽館", "假日")
create_station_train_timetable_if_not_exists("板南線時刻表_頂埔方向_平日", "板南線", "往頂埔", "平日")
create_station_train_timetable_if_not_exists("板南線時刻表_頂埔方向_假日", "板南線", "往頂埔", "假日")

create_station_train_timetable_if_not_exists("淡水信義線時刻表_淡水方向_平日", "淡水信義線", "往淡水", "平日")
create_station_train_timetable_if_not_exists("淡水信義線時刻表_淡水方向_假日", "淡水信義線", "往淡水", "假日")
create_station_train_timetable_if_not_exists("淡水信義線時刻表_象山方向_平日", "淡水信義線", "往象山", "平日")
create_station_train_timetable_if_not_exists("淡水信義線時刻表_象山方向_假日", "淡水信義線", "往象山", "假日")
