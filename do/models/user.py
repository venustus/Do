__author__ = 'venkat'

from mongoengine import *
from mongoengine.django.auth import User
from datetime import datetime


class UserStatus:
    GUEST_USER, ACTIVE_MEMBER, INACTIVE_MEMBER, SUSPENDED, TERMINATED = range(5)


class TeamPrivacyStatus:
    OPEN, OPEN_FOR_REQUESTS, CLOSED = range(3)


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


class Team(Document):
    """
    A team is a group of doers.
    """
    team_id = ObjectIdField()
    team_name = StringField(max_length=64)
    team_email = EmailField()
    team_privacy_status = IntField()
    members = ListField(ReferenceField(Doer))

    class Meta:
        app_label = 'do'