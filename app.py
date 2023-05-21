# -*- coding: utf-8 -*-
import flask
from flask import request, send_from_directory, send_file, abort
import yaml
import os
import datetime
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session

from models import Snapshot
from flask_cors import CORS


app = flask.Flask(__name__)
CORS(app)

# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
home = os.environ.get('HOME')
app.config["REPLICA_FILE"] = f"{home}/replica.my.cnf"
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


# pandas is throwing a numpy deprecation warning
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

periodical_query = """SELECT
	`u`.`user_name`,
    `revs`.`total` AS `user_editcount`,
    `user_properties`.`up_value`
FROM `user` u
LEFT JOIN `user_properties` ON (
  `u`.`user_id` = `user_properties`.`up_user`
  AND `user_properties`.`up_property` = "gender"
)
LEFT JOIN `actor` ON `u`.`user_id` = `actor`.`actor_user`
LEFT JOIN (
  SELECT rev_actor, COUNT(rev_id) as `total`
  FROM revision
  WHERE rev_timestamp > '{period_start}' AND rev_timestamp < '{period_end}'
  GROUP BY rev_actor
) AS `revs` ON `revs`.`rev_actor` = `actor`.`actor_id`
    {tagged_bots}
ORDER BY `revs`.`total` DESC
LIMIT {limit};"""

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
    recentchanges.rc_type < 3
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
    }, poolclass=NullPool)
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


@app.route('/period')
def period():
    wiki = request.args.get('wiki', 'ptwiki')
    limit = request.args.get('limit', '100')
    snapshot_con = create_snapshot_data_connection()
    period_start = request.args.get('period_start', '')
    period_end = request.args.get('period_end', '')
    periodicity = request.args.get('periodicity', '')
    if period_start == '' or period_end == '':
        abort(400, description="period_start and period_end must be set")
    try:
        period_start = datetime.datetime.fromisoformat(period_start)
        period_end = datetime.datetime.fromisoformat(period_end)
        period_start_str = period_start.strftime('%Y%m%d%H%M%S')
        period_end_str = period_end.strftime('%Y%m%d%H%M%S')
    except Exception:
        abort(400, description="Could not parse period start and end, is it in ISO format?")
    if periodicity == 'monthly':
        if not (period_end.day == period_start.day and (
                (period_end.month - period_start.month == 1) and period_end.year == period_start.year) or
                period_start.month - period_end.month == 11 and period_end.year - period_start.year == 1):
            abort(400, "Period should be exactly one month")
    if periodicity == 'weekly':
        if not (period_start.weekday == 0 and period_end.weekday == 0):
            abort(400, "Weekly snapshots should start and end on Mondays")
        if not (period_start - period_end == datetime.timedelta(weeks=1)):
            abort(400, "Weekly snapshots period should be 1 week")
    if periodicity == 'daily':
        if not (period_start - period_end == datetime.timedelta(days=1)):
            abort(400, "Daily snapshots period should be 1 day")

    test, results = maybe_snapshot(
        'periodical', wiki, snapshot_con, limit, period_start=period_start, period_end=period_end,
        periodicity=periodicity)
    if test:
        replicas_con = create_replicas_connection(wiki)
        #  print(periodical_query.format(
        #                  tagged_bots=remove_tagged_bots,
        #                  limit=limit, period_start=period_start_str,
        #                  period_end=period_end_str))
        df = pd.read_sql(periodical_query.format(
                        tagged_bots=remove_tagged_bots,
                        limit=limit, period_start=period_start_str,
                        period_end=period_end_str), replicas_con)
        stats = get_gender_stats(df, limit).to_dict()
        session = Session(bind=snapshot_con)
        snap = Snapshot(
            wiki=wiki,
            type='periodical',
            timestamp=datetime.datetime.now(),
            editors_male=stats['count'].get('male', 0),
            editors_female=stats['count'].get('female', 0),
            editors_neutral=stats['count'].get('neutral', 0),
            edits_male=stats['editcount'].get('male', 0),
            edits_female=stats['editcount'].get('female', 0),
            edits_neutral=stats['editcount'].get('neutral', 0),
            period_start=period_start,
            period_end=period_end,
            limit=limit,
            periodicity=periodicity,
        )
        session.add(snap)
        session.commit()
        results = snap.to_dict()
        session.close()
        replicas_con.dispose()
    snapshot_con.dispose()
    return results

@app.route('/recent')
def recent():
    wiki = request.args.get('wiki', 'ptwiki')
    limit = request.args.get('limit', '100')
    snapshot_con = create_snapshot_data_connection()
    test, results = maybe_snapshot('recent', wiki, snapshot_con, limit)
    if test:
        replicas_con = create_replicas_connection(wiki)
        df = pd.read_sql(recent_changes_query.format(
                        tagged_bots=remove_tagged_bots,
                        limit=limit), replicas_con)
        stats = get_gender_stats(df, limit).to_dict()
        session = Session(bind=snapshot_con)
        snap = Snapshot(
            wiki=wiki,
            type='recent',
            timestamp=datetime.datetime.now(),
            editors_male=stats['count'].get('male', 0),
            editors_female=stats['count'].get('female', 0),
            editors_neutral=stats['count'].get('neutral', 0),
            edits_male=stats['editcount'].get('male', 0),
            edits_female=stats['editcount'].get('female', 0),
            edits_neutral=stats['editcount'].get('neutral', 0),
            limit=limit,
        )
        session.add(snap)
        session.commit()
        results = snap.to_dict()
        session.close()
        replicas_con.dispose()
    snapshot_con.dispose()
    return results


def create_snapshot_data_connection():
    db = app.config['database']
    host = "tools.db.svc.wikimedia.cloud"
    constr = f'mysql+pymysql://{host}/{db}'

    con = create_engine(constr, pool_recycle=60, connect_args={
        'read_default_file': app.config["REPLICA_FILE"],
    }, poolclass=NullPool)
    return con


def maybe_snapshot(
    snapshot_type, wiki, con, limit,
    timedelta=datetime.timedelta(hours=11), period_start=None, period_end=None,
    periodicity=None
):
    session = Session(bind=con)
    if snapshot_type == 'periodical':
        if period_end > datetime.datetime.now():
            abort(400, 'End period is greater than today, count would be incomplete')
        existing_snapshot = session.query(Snapshot).filter(
            Snapshot.wiki == wiki,
            Snapshot.type == snapshot_type,
            Snapshot.limit == limit,
            Snapshot.period_start == period_start,
            Snapshot.period_end == period_end,
            Snapshot.periodicity == periodicity
        )
    else:
        existing_snapshot = session.query(Snapshot).filter(
            Snapshot.wiki == wiki,
            Snapshot.timestamp > datetime.datetime.now() - timedelta,
            Snapshot.type == snapshot_type,
            Snapshot.limit == limit,
        )
    if existing_snapshot.first() is None:
        print('No snapshot, querying replicas')
        session.close()
        return (True, None)
    session.close()
    return (False, existing_snapshot.first().to_dict())


@app.route('/snapshots')
def snapshots():
    wiki = request.args.get('wiki', 'ptwiki')
    type = request.args.get('type', 'recent')
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
    if type == 'periodical':
        snapshots = session.query(Snapshot).filter(
            Snapshot.wiki == wiki,
            Snapshot.period_start > after,
            Snapshot.type == type,
            Snapshot.limit == limit,
        ).order_by(Snapshot.period_start.asc())

    else:
        snapshots = session.query(Snapshot).filter(
            Snapshot.wiki == wiki,
            Snapshot.timestamp >= after,
            Snapshot.timestamp < before,
            Snapshot.type == type,
            Snapshot.limit == limit,
        ).order_by(Snapshot.timestamp.asc())
    out = [snap.to_dict() for snap in snapshots]
    session.close()
    snapshot_con.dispose()
    return out

@app.route('/wikis')
def wikis():
    snapshot_con = create_snapshot_data_connection()
    session = Session(bind=snapshot_con)
    wikis = session.query(Snapshot.wiki).distinct()
    out = [wiki[0] for wiki in wikis]
    session.close()
    snapshot_con.dispose()
    return out

@app.route('/')
def index():
    return send_file('static/lutz/dist/index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static/lutz/dist', path)
