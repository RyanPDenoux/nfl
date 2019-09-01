import requests

import pandas as pd
from bs4 import BeautifulSoup


def clean_player_name(name):
    return name.replace('*', '').replace('+', '')


def scrape_table(url):
    """Provides a soup object for the first table seen"""

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    data_table = soup.find(role='main').find('table')

    return data_table


def parse_data_table(table):
    """parse a bs4 soup table"""

    header = table.find('thead')

    columns = [column.attrs.get('data-stat') for column in header.find_all('th')]

    column_index = columns.index('player') if 'player' in columns else columns.index('team')

    relevant_columns = columns[column_index:]

    body = table.find('tbody')

    players = []
    for row in body.find_all('tr'):

        data = [clean_player_name(column.get_text()) for column in row.find_all('td')]

        if data:
            players.append(data)

    data_frame = pd.DataFrame(players, columns=relevant_columns)

    return data_frame


if __name__ == '__main__':
    passing = 'https://www.pro-football-reference.com/years/2018/passing.htm'
    rushing = 'https://www.pro-football-reference.com/years/2018/rushing.htm'
    receiving = 'https://www.pro-football-reference.com/years/2018/receiving.htm'
    team_defense = 'https://www.pro-football-reference.com/years/2018/opp.htm'
    fantasy = 'https://www.pro-football-reference.com/years/2018/fantasy.htm'

    for url in (passing, rushing, receiving, team_defense, fantasy):
        print(parse_data_table(scrape_website(url)))
