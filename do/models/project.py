__author__ = 'venkat'

from mongoengine import *
from do.models.product import Product
from do.models.user import Doer


class Project(Document):
    project_id = ObjectIdField()
    name = StringField(max_length=64)
    product = ReferenceField(Product)
    start_date = DateTimeField()
    estimated_completion_date = DateTimeField()
    sprint_time_in_weeks = IntField()
    team_name = ReferenceField(Doer)