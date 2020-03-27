'''
- create dated directory in /data
- return current date in fomat %d-%m-%y i.e. 01-03-2020
'''

from datetime import date
import os
import typing

def _create_dated_directory(today: str) -> None:
    if not os.path.exists(f"data/{today}"):
        print(f"Create directory: {today}")
        os.mkdir(f"data/{today}")

def get_date() -> None:
    today = date.today()
    today = today.strftime('%d-%m-%Y')

    _create_dated_directory(today)

    return today
