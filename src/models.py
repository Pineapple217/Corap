from tortoise.models import Model
from tortoise import fields


class Scrape(Model):
    id = fields.IntField(pk=True)
    batch_id = fields.IntField()
    deveui = fields.TextField()
    co2 = fields.SmallIntField()
    temp = fields.DecimalField(max_digits=4, decimal_places=1)
    humidity = fields.SmallIntField()
    time_updated = fields.DatetimeField()
    time_scraped = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.id + " | " + self.deveui


# class Device(Model):
#     room = fields.TextField()
#     deveui = fields.TextField()
#     hashedname = fields.TextField()
