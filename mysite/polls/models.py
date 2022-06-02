from django.db import models

# Create your models here.
class Chart(models.Model):
    data = models.CharField(primary_key=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'chart'

class Stockname(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stockname'