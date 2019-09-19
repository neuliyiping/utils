from django.db import models

# Create your models here.



class Transactions(models.Model):
    title=models.CharField(max_length=32)
    def __str__(self):
        return self.title


class Foodeat(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title