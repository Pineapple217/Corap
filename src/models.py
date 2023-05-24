from tortoise.models import Model
from tortoise import fields


class scrape(Model):
    id = fields.IntField(pk=True)
    deveui = fields.TextField()
    co2 = fields.SmallIntField()
    temp = fields.DecimalField(max_digits=2, decimal_places=1)
    humidity = fields.SmallIntField()
    time_scraped = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.id + " | " + self.deveui
