__author__ = 'venkat'

from mongoengine import *
from task import Task
from product import Product, Component

class BugStatus:
    """
    Bug status.
    """
    UNDER_INSVESTIGATION, CONFIRMED, FIX_READY_NOT_MERGED, FIXED_NOT_VERIFIED, CLOSED_VERIFIED, CANNOT_FIX, \
    NOT_A_BUG_TO_FILER, CANNOT_REPRODUCE_TO_FILER, CLOSED_NOT_REPRODUCIBLE, CLOSED_NOT_A_BUG = range(10)

class Bug(Task):
    """
    A software bug.
    """
    bug_id = ObjectIdField()
    status = IntField()
    product = ReferenceField(Product)
    component = ReferenceField(Component)
    sub_component = ReferenceField(Component)
    security_vulnerability = BooleanField(default=False)

    def set_status(self, status):
        self.status = status

    class Meta:
        app_label = 'do'