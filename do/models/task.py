__author__ = 'venkat'

from datetime import datetime, timedelta
from mongoengine import *
from user import Doer


class TaskUpdate(EmbeddedDocument):
    """
    A single task update by a user.
    """
    content = StringField()
    author = ReferenceField(Doer)
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        app_label = 'do'


class Attachment(EmbeddedDocument):
    """
    Attachments for a task
    """
    name = StringField(max_length=255, required=True)
    data = BinaryField(max_bytes=5000000)

    class Meta:
        app_label = 'do'


class TaskStatus():
    IN_PROGRESS, COMPLETED, OVERDUE, ABORTED = range(4)


class Task(Document):
    """
    Represents an actionable task.
    Title and primary description are required
    """
    id = ObjectIdField()
    title = StringField(max_length=255, required=True)
    created_by = ReferenceField(Doer)
    assignees = ListField(ReferenceField(Doer))
    created_at = DateTimeField(default=datetime.now())
    complete_by = DateTimeField()
    primary_desc = StringField(required=True)
    attachments = ListField(EmbeddedDocumentField(Attachment))
    status = IntField()
    tags = ListField(StringField(max_length=30))
    updates = ListField(EmbeddedDocumentField(TaskUpdate))
    parent_task = ReferenceField('self')
    is_important = BooleanField()
    is_urgent = BooleanField()

    meta = {'allow_inheritance': True}

    def completed(self):
        self.complete_by = datetime.now()
        self.status = TaskStatus.COMPLETED

    def aborted(self):
        self.status = TaskStatus.ABORTED

    def is_completed(self):
        return self.status == TaskStatus.COMPLETED or self.status == TaskStatus.ABORTED

    def is_in_progress(self):
        return self.status == TaskStatus.IN_PROGRESS or self.status == TaskStatus.OVERDUE

    def is_overdue(self):
        time_dif = datetime.now() > self.complete_by
        return time_dif

    def is_due_today(self):
        time_left = ((datetime.now() +
                      timedelta(days=1)).replace(hour=0, minute=0, second=0) - self.complete_by)
        return 1 <= time_left.seconds < 86400

    class Meta:
        app_label = 'do'

