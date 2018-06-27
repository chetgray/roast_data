#!/usr/bin/env python3

import argparse

import dateparser
from googleapiclient.discovery import build
from httplib2 import Http
import oauth2client as oa


def main(secret_path='client_secret.json', db_path='roast_data.sqlite', after_date=None):
    # From https://developers.google.com/gmail/api/quickstart/python
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    store = oa.file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = oa.client.flow_from_clientsecrets(secret_path, SCOPES)
        creds = oa.tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http(cache=".cache")))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Synchronize roast database with latest roast logs.")
    parser.add_argument('--secret', dest='secret_path', default='client_secret.json',
                        help="OAuth client ID file")
    parser.add_argument('--database', dest='db_path', default='roast_data.sqlite',
                        help="SQLite database file")
    parser.add_argument('--after', dest='after_date',
                        type=lambda s: dateparser.parse(s).strftime('%Y/%m/%d'))

    args = parser.parse_args()
    main(secret_path=args.secret_path, db_path=args.db_path, after_date=args.after_date)
