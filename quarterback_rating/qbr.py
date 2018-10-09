import os
import requests
import argparse
import numpy as np
import pandas as pd

from os.path import join
from bs4 import BeautifulSoup
from scipy.stats import gaussian_kde

from bokeh.io import output_file, save, reset_output
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.palettes import Accent5
from bokeh.models import ColumnDataSource


def append_data(dataframe, flag, week):
    files = os.listdir(join(os.getcwd(), 'data'))

    if flag == 'espn':
        if 'espn_qbr.csv' not in files:
            dataframe.to_csv(
                os.path.join(os.getcwd(), 'data', 'espn_qbr.csv'),
                index=False
            )
            print(f'ESPN quarterback stats for week {week}')
            print(dataframe)
            print('Data stored in:',
                  os.path.join(os.getcwd(), 'data', 'espn_qbr.csv'))

        else:
            old = pd.read_csv(os.path.join(
                os.getcwd(), 'data', 'espn_qbr.csv'))
            new = pd.concat([old, dataframe], ignore_index=True)
            new.to_csv(os.path.join(os.getcwd(), 'data', 'espn_qbr.csv'),
                       index=False)

            print(f'ESPN quarterback stats for week {week}')
            print(dataframe)
            print('Data appended to:',
                  os.path.join(os.getcwd(), 'data', 'espn_qbr.csv'))

    elif flag == 'pfr':
        if 'pfr_qbr.csv' not in files:
            dataframe.to_csv(
                os.path.join(os.getcwd(), 'data', 'pfr_qbr.csv'),
                index=False
            )
            print(f'PFR quarterback stats for week {week}')
            print(dataframe)
            print('Data stored in:',
                  os.path.join(os.getcwd(), 'data', 'prf_qbr.csv'))

        else:
            old = pd.read_csv(os.path.join(os.getcwd(), 'data', 'pfr_qbr.csv'))
            new = pd.concat([old, dataframe], ignore_index=True)
            new.to_csv(os.path.join(os.getcwd(), 'data', 'pfr_qbr.csv'),
                       index=False)

            print(f'PFR quarterback stats for week {week}')
            print(dataframe)
            print('Data appended to:',
                  os.path.join(os.getcwd(), 'data', 'pfr_qbr.csv'))


def scrape_ESPN(week):
    page = requests.get(
        f'http://www.espn.com/nfl/qbr/_/type/player-week/week/{week}'
    )

    soup = BeautifulSoup(page.content, 'html.parser')
    quarterback_table = soup.find(id='my-players-table')
    table_data = quarterback_table.find_all('tr')

    data_labels = [
        'player', 'week', 'pts_added', 'pass', 'run', 'penalty', 'total_epa',
        'qb_plays', 'raw_qbr', 'total_qbr'
    ]

    df = pd.DataFrame(columns=data_labels)

    for player in table_data:
        player_data = player.find_all('td')

        player = player_data[1].get_text()
        week_of_play = player_data[2].get_text()
        points_added = player_data[3].get_text()
        passing_yards = player_data[4].get_text()
        rushing_yards = player_data[5].get_text()
        penalty_yards = player_data[6].get_text()
        total_epa = player_data[7].get_text()
        quarterback_plays = player_data[8].get_text()
        raw_qbr = player_data[9].get_text()
        total_qbr = player_data[10].get_text()

        first_name = player
        last_name = ''
        if player != 'PLAYER':
            first_name = player.split()[0]
            last_name = player.split()[1].replace(',', '')

        data = {
            'player': f'{first_name}_{last_name}',
            'week': week_of_play[-1],
            'pts_added': points_added,
            'pass': passing_yards,
            'run': rushing_yards,
            'penalty': penalty_yards,
            'total_epa': total_epa,
            'qb_plays': quarterback_plays,
            'raw_qbr': raw_qbr,
            'total_qbr': total_qbr
        }

        # Only checks first list element for equivalence
        # Eventually need to check against the whole list
        if player != df.columns[0].upper():
            df = df.append(data, ignore_index=True)

    append_data(df, 'espn', week)


def scrape_PFR(week, year=2018):
    page = requests.get(
        'https://www.pro-football-reference.com/play-index/pgl_finder.cgi?'
        f'request=1&match=game&year_min={year}&year_max={year}&'
        'season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&'
        'league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&'
        f'week_num_min={week}&week_num_max={week}&game_day_of_week=&'
        'game_location=&game_result=&handedness=&is_active=&is_hof=&'
        'c1stat=pass_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&'
        'c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&'
        'order_by=pass_rating&from_link=1'
    )

    soup = BeautifulSoup(page.content, 'html.parser')
    quarterback_table = soup.find(id='results')

    table_head = quarterback_table.find('thead')
    head_data = table_head.find_all('tr')

    for data in head_data:
        info = data.find_all('th')

        header_container = [header.get_text() for header in info]

        if header_container[1] == 'Passing':
            next
        else:
            header_container.pop(0)
            header_container[0] = 'player'
            header_container[5] = 'away'

    players = []
    table_body = quarterback_table.find('tbody')
    body_data = table_body.find_all('tr')
    for data in body_data:
        info = data.find_all('td')

        player_container = [i.get_text() for i in info]
        if not player_container:
            next
        else:
            players.append(player_container)

    df = pd.DataFrame(players, columns=header_container)
    df.columns = df.columns.str.lower()
    df.columns.values[3] = 'league'
    df.columns.values[4] = 'team'
    df.columns.values[6] = 'opponent'
    df.columns.values[8] = 'game_number'
    df.columns.values[11] = 'passes_completed'
    df.columns.values[12] = 'passes_attempted'
    df.columns.values[13] = 'completion_percentage'
    df.columns.values[14] = 'yards_from_passing'
    df.columns.values[15] = 'passing_touchdowns'
    df.columns.values[16] = 'interceptions'
    df.columns.values[17] = 'passer_rating'
    df.columns.values[18] = 'sacks_taken'
    df.columns.values[19] = 'yards_lost_to_sacks'
    df.columns.values[20] = 'yards_per_pass'
    df.columns.values[21] = 'adjusted_yards_per_pass'

    append_data(df, 'pfr', week)


def analysis():
    espn = pd.read_csv(join(os.getcwd(), 'data', 'espn_qbr.csv'))
    number_of_weeks = range(1, espn['week'].max() + 1)
    score_to_beat = 60

    for week in number_of_weeks:
        reduced = espn[espn['week'] == week]
        reduced['is_shit'] = reduced.apply(
            lambda x: 'Decent' if x['raw_qbr'] >= score_to_beat
            else 'Dog Shit', axis=1
        )
        distribution_name = f'ESPN Week {week} Distribution'
        hist(reduced, 'raw_qbr', 'is_shit', distribution_name)

        reduced.loc[reduced['player'] == 'Andy_Dalton', 'is_shit'] = 'Dalton'
        ratings_name = f'ESPN Week {week} Raw QBR'
        hbar(reduced, 'raw_qbr', 'player', 'is_shit', ratings_name)

    pfr = pd.read_csv(join(os.getcwd(), 'data', 'pfr_qbr.csv'))
    number_of_weeks = range(1, pfr['week'].max() + 1)
    score_to_beat = 100

    for week in number_of_weeks:
        reduced = pfr[pfr['week'] == week]
        reduced = reduced[reduced['passes_attempted'] > 1]
        reduced['is_shit'] = reduced.apply(
            lambda x: 'Decent' if x['passer_rating'] >= score_to_beat
            else 'Dog Shit', axis=1
        )
        distribution_name = f'PFR Week {week} Distribution'
        hist(reduced, 'passer_rating', 'is_shit', distribution_name)

        reduced.loc[reduced['player'] == 'Andy Dalton', 'is_shit'] = 'Dalton'
        ratings_name = f'PFR Week {week} Passer Rating'
        hbar(reduced, 'passer_rating', 'player', 'is_shit', ratings_name)


def hist(data, attribute, group, name='figure'):
    output = join(os.getcwd(), 'figures', name)
    output_file(output + '.html')

    source = ColumnDataSource(data.groupby(group))

    x = np.linspace(0, data[attribute].max(), data[attribute].max())
    pdf = gaussian_kde(data[attribute])

    plot = figure(
        title=name,
        x_axis_label=attribute
    )

    hist, edges = np.histogram(
        data[attribute], density=True, bins=12
    )
    plot.quad(
        top=hist,
        bottom=0,
        left=edges[:-1],
        right=edges[1:],
        alpha=0.4
    )

    plot.line(x, pdf(x))

    save(plot)
    reset_output()


def hbar(data, attribute, index, category, name=None):
    output = join(os.getcwd(), 'figures', name)
    output_file(output + '.html')

    source = data.sort_values(by=attribute, ascending=True)
    cmap = factor_cmap(
        category,
        palette=Accent5,
        factors=sorted(source[category].unique())
    )

    plot = figure(
        y_range=source[index],
        title=name,
        x_axis_label=attribute,
        tooltips=[(attribute.replace('_', ' '), f'@{attribute}')]
    )
    plot.hbar(
        y=index, right=attribute, height=0.8, source=source,
        fill_color=cmap, line_color=cmap
    )

    save(plot)
    reset_output()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--espn', action='store_true',
                        help='designates espn')
    parser.add_argument('-p', '--pfr', action='store_true',
                        help='designates pfr')
    parser.add_argument('-w', '--week', type=int,
                        help='week of the NFL season')
    args = parser.parse_args()

    if args.week is None:
        if args.espn:
            print('please select a week to scrape data from')

        elif args.pfr:
            print('please select a week to scrape data from')

        else:
            analysis()

    elif args.espn:
        scrape_ESPN(args.week)

    elif args.pfr:
        scrape_PFR(args.week)
