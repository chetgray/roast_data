#!/usr/bin/env python3

import argparse

import dateparser


def main(secret_path='client_secret.json', db_path='roast_data.sqlite', after_date=None):
    pass


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
