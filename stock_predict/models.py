import json

from django.db import models


# Create your models here.
class Company(models.Model):
    stock_code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

class StockIndex(models.Model): #用company去找stock
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    Date = models.CharField(max_length=30) # 日期
    Score_Strength = models.FloatField(default=0)
    Score_Trend = models.FloatField(default=0)
    Score_Funds = models.FloatField(default=0)
    Score_Expectation = models.FloatField(default=0)
    Score_Risk = models.FloatField(default=0)
    Score_Comprehensive = models.FloatField(default=0)
    class Meta:
        unique_together = ('company', 'Date')  # 唯一約束只有一個防止重複

    def __str__(self):
        return f"{self.company.stock_code} - {self.Date}"


class HistoryData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data = models.TextField() # string 
    start_date = models.CharField(max_length=30)

    def set_data(self,list_data):   # set list as a string store 
        try:
            start_da = list_data[0][0]  # list first date
            data_json = json.dumps(list_data)  # list dict to string
        except (KeyError,TypeError,IndexError):
            raise Exception("list_data must be 2 dimensions list.")
        else:
            self.start_date = start_da
            self.data = data_json

    def get_data(self):
        return json.loads(self.data)        # sting to dict/list

class PredictData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data = models.TextField() 
    start_date = models.CharField(max_length=30)

    def set_data(self, list_data):
        try:
            st_da = list_data[0][0] 
            data_json = json.dumps(list_data)  
        except (KeyError,TypeError):
            raise Exception("list_data must be 2 dimensions list.")
        else:
            self.start_date = st_da
            self.data = data_json

    def get_data(self):
        return json.loads(self.data) 
