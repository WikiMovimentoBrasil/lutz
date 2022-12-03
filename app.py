# -*- coding: utf-8 -*-
import flask
from flask import request
import yaml
import os
import pandas as pd
import pymysql

app = flask.Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
home = os.environ.get('HOME')
app.config["REPLICA_FILE"] = f"{home}/replica.my.cnf"
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


DATABASE = '{wiki}_p'
# con = create_engine(constr, pool_recycle= 60)

remove_tagged_bots = '''left join
        user_groups ug
            on (
                u.user_id=ug.ug_user
                and ug_group = "bot"
            )
    left join
        user_former_groups ufg
            on (
              u.user_id=ufg.ufg_user
              and ufg_group = "bot"
            )
    WHERE
        ug_group is null and ufg_group is null'''

historical_query = """select
        user_editcount,
        user_name,
        up_value
    from
        user u
    left join
        user_properties up
            ON (
                u.user_id=up.up_user
                and up_property = "gender"
            )
         {tagged_bots}
    ORDER BY
        user_editcount desc
      limit {limit};"""

recent_changes_query = '''
select count(rc_id) as user_editcount, u.user_name, up.up_value
from recentchanges
left join
    actor
        ON (
            recentchanges.rc_actor=actor.actor_id
            )
left join
    user u
        ON (
            actor.actor_user=u.user_id
            )
left join
    user_properties up
        ON (
            u.user_id=up.up_user
            and up_property = "gender"
        )
        {tagged_bots}
    AND
    recentchanges.rc_type != 5
GROUP BY recentchanges.rc_actor
ORDER BY
    user_editcount desc
limit {limit}
'''


def create_connection(wiki):
    db = DATABASE.format(wiki=wiki)
    con = pymysql.connect(host=f"{wiki}.analytics.db.svc.wikimedia.cloud",
                          read_default_file=app.config["REPLICA_FILE"],
                          database=db)
    return con


def get_gender_stats(df, limit):
    """Gets gender stats from query dataframe"""
    limit = int(limit)

    df['up_value'] = df['up_value'].fillna(b'neutral')
    df['up_value'] = df['up_value'].str.decode("utf-8")
    df['user_name'] = df['user_name'].str.decode("utf-8")

    describe = df.groupby(df['up_value']).describe()
    describe.loc[:, ('user_editcount', '%_of_editors')] = describe[
        'user_editcount']['count']/limit * 100
    total_edits = df.loc[:, 'user_editcount'].sum()
    describe = pd.concat([describe, df.groupby('up_value').sum()], axis=1
                         ).reindex(describe.index)
    describe.loc[:, ('%_of_edits')] = describe.loc[:, ('user_editcount'
                                                       )]/total_edits * 100
    out = describe.loc[:, [('user_editcount', '%_of_editors'),
                           ('user_editcount', 'count'), 'user_editcount',
                           '%_of_edits']]
    out.columns = (['%_of_editors', 'count', 'editcount', '%_of_edits'])
    return out


@app.route('/historical')
def historical():
    wiki = request.args.get('wiki', 'ptwiki')
    limit = request.args.get('limit', '100')
    con = create_connection(wiki)
    df = pd.read_sql(historical_query.format(tagged_bots=remove_tagged_bots,
                     limit=limit), con)
    return get_gender_stats(df, limit).to_json()
