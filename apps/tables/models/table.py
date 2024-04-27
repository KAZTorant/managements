from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.CharField(max_length=10, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    room = models.ForeignKey(
        Room,
        related_name='tables',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"Table {self.number} in {self.room.name if self.room else 'No Room'}"
