from mongoengine import EmailField, StringField
from do.models.task import Task

__author__ = 'venkat'

import imaplib
import datetime
import email
import base64

from do.models.user import Doer

email_subject_prefix = '=?UTF-8?B?'
email_subject_suffix = '?='


class EmailTaskListener:
    _server_name = ''
    _server_port = ''
    _email = ''
    _password = ''
    _imap = None

    def __init__(self, server_name, server_port, email, password):
        self._server_name = server_name
        self._server_port = server_port
        self._email = email
        self._password = password
        self._imap = imaplib.IMAP4_SSL(self._server_name, self._server_port)
        self._imap.login(self._email, self._password)
        self._imap.select('inbox')

    def get_email_one_day(self, user):
        date = (datetime.date.today() - datetime.timedelta(1)).strftime('%d-%b-%Y')
        result, data = self._imap.uid('search', None, '(SENTSINCE {date})'.format(date=date))
        latest_email_uid = data[0].split()[-1]
        result, data = self._imap.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        print 'Raw email received: ' + raw_email
        email_message = email.message_from_string(raw_email)

        subject = email_message['Subject']
        if subject.startswith(email_subject_prefix):
            subject = base64.b64decode(subject[len(email_subject_prefix):len(subject) - len(email_subject_suffix)])
        task = EmailTask(from_id=email.utils.parseaddr(email_message['From'])[1],
                         to_list=email_message['To'],
                         title=subject,
                         primary_desc=raw_email,
                         created_at=datetime.datetime.now(),
                         assignees=[Doer.objects.get(username=user.username)])
        task.save()


class EmailTask(Task):
    """
    Represents an actionable email.
    Title is the subject of the email.
    Primary description is the body.
    """
    from_id = EmailField()
    to_list = StringField()
    cc_list = StringField()
    bcc_list = StringField()

    class Meta:
        app_label = 'do'