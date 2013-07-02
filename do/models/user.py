__author__ = 'venkat'

from mongoengine import *
from mongoengine.django.auth import User
from datetime import datetime

class UserStatus:
    GUEST_USER, ACTIVE_MEMBER, INACTIVE_MEMBER, SUSPENDED, TERMINATED = range(5)

class Doer(User):
    """
    A user who does creative tasks.
    This extends the mongoengine User model.
    """
    status = IntField()
    terminated_date = None
    manager = ReferenceField('Doer')

    def is_terminated(self):
        if self.terminated_date is not None:
            return self.terminated_date < datetime.now()
        else:
            return False

    def terminate(self):
        self.terminated_date = DateTimeField(default=datetime.now())
        self.status = UserStatus.TERMINATED

    class Meta:
        app_label = 'do'
