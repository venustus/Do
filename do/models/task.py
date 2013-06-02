__author__ = 'venkat'

from datetime import datetime
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
    title = StringField(max_length=255, required=True)
    created_by = ReferenceField(Doer)
    assignees = ListField(ReferenceField(Doer))
    created_at = DateTimeField(default=datetime.now())
    complete_by = DateTimeField()
    primary_desc = StringField(max_length=20000, required=True)
    attachments = ListField(EmbeddedDocumentField(Attachment))
    status = IntField()
    tags = ListField(StringField(max_length=30))
    updates = ListField(EmbeddedDocumentField(TaskUpdate))

    meta = {'allow_inheritance': True}

    def completed(self):
        self.complete_by = datetime.now()
        self.status = TaskStatus.COMPLETED

    def aborted(self):
        self.status = TaskStatus.ABORTED

    class Meta:
        app_label = 'do'