from __future__ import print_function

import vision
import base64
import os.path

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


user_id = 'me'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)


def prepare_inbox():
    unread_msgs = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()

    if 'messages' in unread_msgs:
        messages_list = unread_msgs['messages']

        for msg in messages_list:
            m_id = msg['id']  # get id of individual message

            service.users().messages().modify(userId=user_id, id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()

            message = service.users().messages().get(userId=user_id, id=m_id).execute()
            payload = message['payload']
            headers = payload['headers']

            for header in headers:  # getting the Subject
                if header['name'] == 'Subject':
                    msg_subject = header['value']
                    if not ('Screenshot' in msg_subject):
                        continue

            for part in payload['parts']:
                if part['filename']:
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(userId=user_id, messageId=m_id, id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                    with open('input.png', 'wb') as f:
                        f.write(file_data)

                    vision.prepare_screenshot('input.png')
