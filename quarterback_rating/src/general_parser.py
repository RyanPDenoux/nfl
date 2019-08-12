import requests

import pandas as pd
from bs4 import BeautifulSoup


def scrape_website(url):
    """Provides a soup object given a url"""

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    data_table = soup.find(role='main').find('table')

    return data_table


def parse_data_table(table):
    """parse a bs4 soup table"""

    header = table.find('thead')
    columns = [column.attrs.get('data-stat') for column in header.find_all('th')]

    relevant_columns = columns[columns.index('player'):]

    body = table.find('tbody')

    players = []
    for row in body.find_all('tr'):

        # TODO treat string fields before loading into Pandas
        player = [column.get_text() for column in row.find_all('td')]

        if player:
            players.append(player)

    data_frame = pd.DataFrame(players, columns=relevant_columns)

    return data_frame


if __name__ == '__main__':
    passing = 'https://www.pro-football-reference.com/years/2018/passing.htm'
    rushing = 'https://www.pro-football-reference.com/years/2018/rushing.htm'
    receiving = 'https://www.pro-football-reference.com/years/2018/receiving.htm'
    fantasy = 'https://www.pro-football-reference.com/years/2018/fantasy.htm'

    for url in (passing, rushing, receiving, fantasy):
        dt = scrape_website(url)
        parse_data_table(dt)
