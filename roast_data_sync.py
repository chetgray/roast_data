#!/usr/bin/env python3

import argparse
from base64 import urlsafe_b64decode
import datetime
import sqlite3

import dateparser
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import (file as oafile,
                          client as oaclient,
                          tools as oatools)


def create_tables(con):
    with con: # commit on success, rollback on exception
        con.execute('''
            CREATE TABLE IF NOT EXISTS message (
                id TEXT PRIMARY KEY,
                snippet TEXT,
                internal_date TIMESTAMP, -- Works with sqlite3.PARSE_DECLTYPES
                attachment_id TEXT)
            ''')
        con.execute('''
            CREATE TABLE IF NOT EXISTS message_data (
                message_id TEXT PRIMARY KEY REFERENCES message(id) ON DELETE CASCADE ON UPDATE CASCADE,
                data TEXT)
            ''')


def import_csvs(con, csv_files):
    raise NotImplementedError


def main(db_path='roast_data.sqlite', secret_path='client_secret.json',
         after_date=datetime.date.min.strftime('%Y/%m/%d'),
         before_date=datetime.date.max.strftime('%Y/%m/%d'),
         csv_files=None):
    con = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    create_tables(con)

    if csv_files:
        import_csvs(con, csv_files)
    else:
        # From https://developers.google.com/gmail/api/quickstart/python
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = oafile.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = oaclient.flow_from_clientsecrets(secret_path, SCOPES)
            creds = oatools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http(cache=".cache")))
        message_resource = service.users().messages()
        list_request = message_resource.list(userId='me',
                                             q='from:lsr@smartroaster.com '
                                               'has:attachment '
                                               f'after:{after_date} '
                                               f'before:{before_date}')
        while list_request is not None:
            list_response = list_request.execute()
            for message in list_response['messages']:
                message_id = message['id']
                print(message_id, end=' ')
                row = con.execute('SELECT internal_date'
                                  '  FROM message'
                                  '  WHERE id == ?',
                                  (message_id,)).fetchone()
                if row is not None:
                    print(f"{row[0]} exists")
                    continue
                full_message = message_resource.get(userId='me', id=message_id).execute()
                # Fun little use of __next__ on a filtered generator
                attachment_id = next((part for part in full_message['payload']['parts'] if part['filename']), None)['body']['attachmentId']
                internal_date = datetime.datetime.fromtimestamp(int(full_message['internalDate'])/1000)
                print(f"{internal_date} downloading...")
                con.execute('INSERT INTO message (id, snippet, internal_date, attachment_id) '
                            'VALUES (?, ?, ?, ?)',
                            (message_id,
                             full_message['snippet'],
                             internal_date,
                             attachment_id))
                attachment = message_resource.attachments().get(
                    userId='me',
                    messageId=message_id,
                    id=attachment_id).execute()
                data = urlsafe_b64decode(attachment['data']).decode()
                con.execute('INSERT INTO message_data (message_id, data) '
                            'VALUES (?, ?)',
                            (message_id, data))
                con.commit()
            else:
                list_request = message_resource.list_next(list_request, list_response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Synchronize roast database with latest roast logs.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--database', dest='db_path', default='roast_data.sqlite',
                        help="SQLite database file")
    parser.add_argument('--secret', dest='secret_path', default='client_secret.json',
                        help="OAuth client ID file")
    parser.add_argument('--after', dest='after_date',
                        default=datetime.date.min,
                        type=lambda s: dateparser.parse(s).strftime('%Y/%m/%d'))
    parser.add_argument('--before', dest='before_date',
                        default=datetime.date.max,
                        type=lambda s: dateparser.parse(s).strftime('%Y/%m/%d'))
    parser.add_argument('csv_files', nargs='*', type=argparse.FileType('r'),
                        help="**NOT IMPLEMENTED** CSV file(s) to import")

    args = parser.parse_args()
    main(db_path=args.db_path, secret_path=args.secret_path,
         after_date=args.after_date, before_date=args.before_date,
         csv_files=args.csv_files)
