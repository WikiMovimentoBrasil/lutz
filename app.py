# -*- coding: utf-8 -*-
import flask
from flask import request
import yaml
import os
import datetime
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Snapshot


app = flask.Flask(__name__)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
home = os.environ.get('HOME')
app.config["REPLICA_FILE"] = f"{home}/replica.my.cnf"
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


# pandas is giving throwing a numpy deprecation warning
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

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


def create_replicas_connection(wiki):
    db = DATABASE.format(wiki=wiki)
    host = f"{wiki}.analytics.db.svc.wikimedia.cloud"
    constr = f'mysql+pymysql://{host}/{db}'

    con = create_engine(constr, pool_recycle=60, connect_args={
        'read_default_file': app.config["REPLICA_FILE"],
    })
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
    describe = pd.concat([describe, df.groupby('up_value').sum(
        numeric_only=True)],
        axis=1).reindex(describe.index)
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
    con = create_replicas_connection(wiki)
    df = pd.read_sql(historical_query.format(tagged_bots=remove_tagged_bots,
                     limit=limit), con)
    return get_gender_stats(df, limit).to_json()


@app.route('/recent')
def recent():
    wiki = request.args.get('wiki', 'ptwiki')
    limit = request.args.get('limit', '100')
    replicas_con = create_replicas_connection(wiki)
    df = pd.read_sql(recent_changes_query.format(
                     tagged_bots=remove_tagged_bots,
                     limit=limit), replicas_con)
    snapshot_con = create_snapshot_data_connection()
    test, results = maybe_snapshot('recent', wiki, snapshot_con, limit)
    if test:
        stats = get_gender_stats(df, limit).to_dict()
        session = Session(bind=snapshot_con)
        snap = Snapshot(
            wiki=wiki,
            type='recent',
            timestamp=datetime.datetime.now(),
            editors_male=stats['count']['male'],
            editors_female=stats['count']['female'],
            editors_neutral=stats['count']['neutral'],
            edits_male=stats['editcount']['male'],
            edits_female=stats['editcount']['female'],
            edits_neutral=stats['editcount']['neutral'],
            limit=limit,
        )
        session.add(snap)
        session.commit()
        results = snap.to_dict()
        session.close()
    return results


def create_snapshot_data_connection():
    db = app.config['database']
    host = "tools.db.svc.wikimedia.cloud"
    constr = f'mysql+pymysql://{host}/{db}'

    con = create_engine(constr, pool_recycle=60, connect_args={
        'read_default_file': app.config["REPLICA_FILE"],
    })
    return con


def maybe_snapshot(
    snapshot_type, wiki, con, limit,
    timedelta=datetime.timedelta(hours=11)
):
    session = Session(bind=con)
    existing_snapshot = session.query(Snapshot).filter(
        Snapshot.wiki == wiki,
        Snapshot.timestamp > datetime.datetime.now() - timedelta,
        Snapshot.type == snapshot_type,
        Snapshot.limit == limit,
    )
    if existing_snapshot.first() is None:
        session.close()
        return (True, None)
    session.close()
    return (False, existing_snapshot.first().to_dict())


@app.route('/snapshots')
def snapshots():
    wiki = request.args.get('wiki', 'ptwiki')
    snapshot_type = request.args.get('snapshot_type', 'recent')
    limit = request.args.get('limit', '100')
    before = request.args.get('before', '')
    if before == '':
        before = datetime.datetime.now()
    else:
        try:
            before = datetime.datetime.fromisoformat(before)
        except Exception:
            raise TypeError("Before date cannot be parsed. Is it ISO 8601?")
    after = request.args.get('after', '')
    if after == '':
        after = datetime.datetime.now() - datetime.timedelta(days=30)
    else:
        try:
            after = datetime.datetime.fromisoformat(after)
        except Exception:
            raise TypeError("After date cannot be parsed. Is it ISO 8601?")
    snapshot_con = create_snapshot_data_connection()

    session = Session(bind=snapshot_con)
    snapshots = session.query(Snapshot).filter(
        Snapshot.wiki == wiki,
        Snapshot.timestamp >= after,
        Snapshot.timestamp < before,
        Snapshot.type == snapshot_type,
        Snapshot.limit == limit,
    )
    session.close()
    return [snap.to_dict() for snap in snapshots]
