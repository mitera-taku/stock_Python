from django.db import models

class Stock(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    latest_price = models.FloatField()

    def __str__(self):
        return self.name

class StockHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.BigIntegerField()

    def __str__(self):
        return f"{self.stock.name} on {self.date}"
