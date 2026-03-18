from django.db import models

# Create your models here.
class Line(models.Model):
    line_name = models.CharField(max_length = 10) # 捷運線名字(淡水信義線)

    def __str__(self):
        return self.line_name  # 返回線路名稱作為顯示內容

class Direction(models.Model):
    direction_name = models.CharField(max_length = 10) # 方向名稱(往淡水)
    line_name = models.ForeignKey(Line, related_name='directions', on_delete=models.CASCADE) # 屬於哪一個捷運線

    def __str__(self):
        return f"{self.line_name}-{self.direction_name}" # 返回線路名稱以及方向作為顯示內容

class Station(models.Model):
    station_name = models.CharField(max_length = 10) # 捷運站名稱(R28淡水)
    line_name = models.ForeignKey(Line, related_name='stations', on_delete=models.CASCADE) # 屬於哪一個捷運線

    def __str__(self):
        return self.station_name

class Train(models.Model):
    train_number = models.IntegerField() # 某某方向的第幾台捷運
    direction_name = models.ForeignKey(Direction, related_name='trains', on_delete=models.CASCADE) # 屬於哪個方向的車次
    day_type = models.CharField(max_length = 10) # 平日/假日
    
    def __str__(self):
        return f"{self.day_type}{self.direction_name}的第{self.train_number}班車"

class Timetable(models.Model):
    train_number = models.ForeignKey(Train, related_name='timetables', on_delete=models.CASCADE) # 某某方向的第幾台捷運
    station_name = models.ForeignKey(Station, on_delete=models.CASCADE) # # 捷運站名稱(R28淡水)
    arrival_time = models.TimeField() # 捷運抵達車站時間

    def __str__(self):
        return f"{self.train_number} {self.arrival_time} 抵達{self.station_name}"