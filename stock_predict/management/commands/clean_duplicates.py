# stock_predict/management/commands/clean_duplicates.py
# 這是刪除資料庫重複的python
from django.core.management.base import BaseCommand
from stock_predict.models import StockIndex
from django.db.models import Count

class Command(BaseCommand):
    help = '清理StockIndex模型中的重複紀錄' #清理StockIndex模型中的重複紀錄

    def handle(self, *args, **options):
        # 查找重複的 (company, Date) 组合
        duplicates = StockIndex.objects.values('company', 'Date').annotate(count=Count('id')).filter(count__gt=1)
        
        for dup in duplicates:
            company_id = dup['company']
            date = dup['Date']
            # 獲取所有重複紀錄，按照id降續排序，只留最新的 
            duplicate_records = StockIndex.objects.filter(company_id=company_id, Date=date).order_by('-id')
            duplicate_records = list(duplicate_records)  # 轉成List
            
            # 只留第一條其他全刪除
            for record in duplicate_records[1:]:
                record.delete()
                self.stdout.write(f"刪除重複紀錄: 公司ID {company_id}, 日期 {date}, 紀錄ID {record.id}")
        
        self.stdout.write("重複紀錄清理完成")