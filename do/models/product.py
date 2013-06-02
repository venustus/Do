__author__ = 'venkat'

from mongoengine import *
from user import User

class ProductStatus:
    DEVELOPMENT, BETA, PRODUCTION = range(3)

class Component(Document):
    component_id = ObjectIdField()
    name = StringField(max_length=64)
    default_assignee = ReferenceField(User)
    sub_components = ListField(ReferenceField('Component'))

    class Meta:
        app_label = 'do'

class Product(Document):
    product_id = ObjectIdField()
    product_name = StringField(max_length=64)
    product_category = StringField(max_length=64)
    version = StringField(max_length=64)
    status = IntField()
    default_assignee = ReferenceField(User)
    component_list = ListField(ReferenceField(Component))


    class Meta:
        app_label = 'do'
