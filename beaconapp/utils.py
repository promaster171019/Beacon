import httplib2
import os
from datetime import datetime, time

from weasyprint import HTML
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from google.oauth2 import id_token
from google.auth.transport import requests

from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string

from beaconapp.models import Pdf


def convert_to_date(date):
    """"
    Takes date in format mm/dd/yyyy
    Returns datetime object
    """
    if not date:
        return ''
    month, day, year = [int(val) for val in date.split('/')]
    return datetime(year, month, day)


def get_time(time_string):
    hours, minutes = [int(x) for x in time_string.split(':')]
    return time(hours, minutes)


def request_validator(request, *args):
    """
    Validate param in request.data
    :param request:
    :param args: fields to validate
    :return:
    """
    broken = []
    for param in args:
        if not request.data.get(param, None):
            broken.append(param)
    return broken


def create_pdf(html, name, pdf_type, event, student=None):
    """
    Creating pdf
    :param html: html template
    :param name: name of created file
    :param pdf_type: type of pdf: break, discontinuation, upgrade
    :param event: event what should be connected with pdf
    :param student: student instance
    :return:
    """
    try:
        pdf_file = ContentFile(
            HTML(string=html).write_pdf()
        )
        pdf_file.name = '{}.pdf'.format(name)

        pdf = Pdf()
        pdf.name = name
        pdf.type = pdf_type
        pdf.file = pdf_file
        pdf.event = event

        if student:
            pdf.student = student

        pdf.save()

        return pdf
    except Exception as e:
        print(e)
        return None


def send_email(subject, template, send_from, send_to, context, html=False):
    """

    :param subject:
    :param template:
    :param send_from:
    :param send_to:
    :param context:
    :return:
    """

    """An app-specific wrapper around Django's send_mail function.

    Block real emails from being sent to fake users in testing.
    """
    assert isinstance(send_to, (list, tuple, str)), \
        'send_to must be an instance of list, tuple, or str'

    if isinstance(send_to, str):
        send_to = [send_to]

    send_to = ([email for email in send_to])
    body = render_to_string(template, context)
    connection = get_connection(
        fail_silently=False,
    )


    mail = EmailMultiAlternatives(subject, body,
                                  send_from, send_to,
                                  connection=connection)
    if (html):
        html_email = render_to_string(template, context)
        mail.attach_alternative(html_email, 'text/html')

    return mail.send()


def get_gapi_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = os.path.join(settings.BASE_DIR, '{}'.format(settings.CLIENT_SECRET_FILE))
    store = Storage(credential_path)
    try:
        credentials = store.get()
    except Exception as ex:
        credentials = None
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(settings.CLIENT_SECRET_FILE, settings.SCOPES)
        flow.user_agent = settings.APPLICATION_NAME
        flags = tools.argparser.parse_args(args=[])
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def prepare_data_and_create_event(event_name, event_location, start_date, start_time,
                                  end_time, description, attendees, instance):
    """
    Create dict and call method to send it to create events google calendar
    :param event_name:
    :param event_location:
    :param start_date: first date of class
    :param start_time: start time of each class
    :param end_time: end time of each class
    :param description:
    :param attendees:
    :param instance: class instance
    :return: None
    """
    startdate_starttime = '{}{}'.format(
        start_date.strftime("%Y-%m-%dT"),
        start_time.strftime("%H:%M:%S")
    )
    startdate_endtime = '{}{}'.format(
        start_date.strftime("%Y-%m-%dT"),
        end_time.strftime("%H:%M:%S")
    )

    sample_event = {
        'summary': event_name,
        'location': event_location.long_name,
        'description': description,
        'start': {
            'dateTime': startdate_starttime,  # '2017-11-30T09:00:00',
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': startdate_endtime,  # '2017-11-30T10:00:00',
            'timeZone': 'America/New_York',
        },
        'attendees': attendees,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    calendar_id = event_location.calendarId if event_location.calendarId else 'primary'
    event = create_gcalendar_event(sample_event, calendar_id)

    instance.gc_event_id = event.get('id')
    instance.save()


def prepare_data_and_create_parent_event(calendar_id, event_name, event_location_name, start_date,
                                         start_time, end_time, description, attendees, instance):
    """
    Create dict and call method to send it to create events google calendar
    :param calendar_id:
    :param event_name:
    :param event_location_name:
    :param start_date: first date of class
    :param start_time: start time of each class
    :param end_time: end time of each class
    :param description:
    :param attendees:
    :return: None
    """
    startdate_starttime = '{}{}'.format(
        start_date.strftime("%Y-%m-%dT"),
        start_time.strftime("%H:%M:%S")
    )
    startdate_endtime = '{}{}'.format(
        start_date.strftime("%Y-%m-%dT"),
        end_time.strftime("%H:%M:%S")
    )

    sample_event = {
        'summary': event_name,
        'location': event_location_name,
        'description': description,
        'start': {
            'dateTime': startdate_starttime,
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': startdate_endtime,
            'timeZone': 'America/New_York',
        },
        'attendees': attendees,
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    calendar_id = calendar_id if calendar_id else 'primary'
    event = create_gcalendar_event(sample_event, calendar_id)

    instance.gc_parent_event_id = event.get('id')
    instance.save()


def prepare_data_and_update_event(event_id, calendar_id, event_name=None, description=None,
                                  event_location=None, start_date=None, start_time=None,
                                  end_time=None, attendees=None):
    """
    Create dict and call method to send it to update events google calendar
    :param event_id: required
    :param calendar_id: required
    :param event_name:
    :param description:
    :param event_location:
    :param start_date: first date of class
    :param start_time: start time of each class
    :param end_time: end time of each class
    :param attendees:
    :return: None
    """
    event = {}

    if event_name:
        event['summary'] = event_name

    if event_location:
        event['location'] = event_location.long_name

    if description:
        event['description'] = description

    if attendees:
        event['attendees'] = attendees

    if start_date and start_time and end_time:
        event['start'] = {
            'dateTime': '{}{}'.format(
                start_date.strftime("%Y-%m-%dT"),
                start_time.strftime("%H:%M:%S")
            ),
            'timeZone': 'America/New_York',
        }
        event['end'] = {
            'dateTime': '{}{}'.format(
                start_date.strftime("%Y-%m-%dT"),
                end_time.strftime("%H:%M:%S")
            ),
            'timeZone': 'America/New_York',
        }

    calendar_id = calendar_id if calendar_id else 'primary'
    update_gcalendar_event(calendar_id, event_id, event)


def create_gcalendar_event(event_dict, calendar_id):
    """
    Create event in Google Calendar
    :param event_dict: data to create event
    :param calendar_id: Google Calendar identifier
    :return: Google Calendar event dict
    """
    credentials = get_gapi_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().insert(calendarId=calendar_id,
                                    body=event_dict,
                                    sendNotifications=False).execute()
    return event


def get_gcalendar_event(calendar_id, event_id):
    """
    Create event in Google Calendar
    :param calendar_id: Google Calendar identifier
    :param event_id: Google Calendar event id
    :return: Google Calendar event dict
    """
    credentials = get_gapi_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().get(calendarId=calendar_id,
                                 eventId=event_id,
                                 sendNotifications=False).execute()
    return event


def get_gcalendar_event_instances(calendar_id, event_id):
    """
    Returns instances of the specified recurring event
    :param calendar_id:
    :param event_id:
    :return:
    """
    credentials = get_gapi_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event_instances = service.events().instances(calendarId=calendar_id,
                                                 eventId=event_id) \
                                      .execute()
    return event_instances['items']


def update_gcalendar_event(calendar_id, event_id, event_dict):
    """
    Update event in Google Calendar
    :param calendar_id: Google Calendar identifier
    :param event_id: Google Calendar event id
    :param event_dict: data to create event
    :return: Google Calendar event dict
    """
    credentials = get_gapi_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().patch(calendarId=calendar_id,
                                   eventId=event_id,
                                   body=event_dict,
                                   sendNotifications=False).execute()
    return event


def delete_gcalendar_event(calendar_id, event_id):
    """
    Deletes an event by id
    :param calendar_id:
    :param event_id:
    :return:
    """
    credentials = get_gapi_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


def split_and_strip_raw(arr, divider):
    """
    Split and strip row to array
    :param arr: array to split
    :param divider: divide row by this symbol/symbols
    :return:
    """
    return [x.strip() for x in arr.split(divider)]


def convert_str_for_pdf_name(string):
    """
    Bringing the line to the desired format
    for the name pdf file
    :param string: str
    :return: str
    """

    return string.replace(' ', '-').lower()


def validation_token_by_google(token):
    """
    Validation a token by the google oauth
    :param token: str
    :return: email string
    """
    client_id = settings.GOOGLE_APPLICATION_CREDENTIALS['web']['client_id']
    email = None

    try:
        info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        email = info['email']
    except Exception as e:
        print("Token error validation by google: {}".format(e))

    return email
