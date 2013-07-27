__author__ = 'venkat'

from mongoengine import *
from do.models.product import Product
from do.models.user import Doer


class Project(Document):
    project_id = ObjectIdField()
    name = StringField(max_length=64)
    product = ReferenceField(Product)
    start_date = DateTimeField()
    estimated_time_for_completion_weeks = IntField()
    sprint_time_in_weeks = IntField()
    members = ListField(ReferenceField(Doer))

    class Meta:
        app_label = 'do'