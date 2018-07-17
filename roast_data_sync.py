#!/usr/bin/env python3

import argparse
import datetime
import sqlite3

import dateparser
from googleapiclient.discovery import build
from httplib2 import Http
import oauth2client as oa


def main(db_path='roast_data.sqlite', secret_path='client_secret.json',
         after_date=datetime.date.min.strftime('%Y/%m/%d'),
         csv_files=None):
    con = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
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

    if csv_files:
        pass
    else:
        # From https://developers.google.com/gmail/api/quickstart/python
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = oa.file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = oa.client.flow_from_clientsecrets(secret_path, SCOPES)
            creds = oa.tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http(cache=".cache")))
        latest_stored_message_id = con.execute('SELECT id from message ORDER BY internal_date DESC LIMIT 1').fetchone()[0]
        message_resource = service.users().messages()
        list_request = message_resource.list(userId='me',
                                             q='from:lsr@smartroaster.com '
                                               'has:attachment '
                                               'after:{}'.format(after_date))
        while list_request is not None:
            list_response = list_request.execute()
            for message in list_response['messages']:
                if message['id'] == latest_stored_message_id:
                    list_request = None
                    break
                full_message = message_resource.get(userId='me', id=message['id']).execute()
                con.execute('INSERT INTO message (id, snippet, internal_date, attachment_id) '
                            'VALUES (?, ?, ?, ?)',
                            (message['id'],
                             full_message['snippet'],
                             datetime.fromtimestamp(full_message['internalDate']/1000),
                             # Pull the attachment_id from the first part with a filename
                             next((part for part in full_message['payload']['parts'] if part['filename']), None)['body']['attachmentId']
                            ))
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
                        default=datetime.date.min.strftime('%Y/%m/%d'),
                        type=lambda s: dateparser.parse(s).strftime('%Y/%m/%d'))
    parser.add_argument('csv_files', nargs='*', type=argparse.FileType('r'),
                        help="CSV file(s) to import")

    args = parser.parse_args()
    main(db_path=args.db_path, secret_path=args.secret_path,
         after_date=args.after_date, csv_files=args.csv_files)
