"""Validate the existing public goal sheet without inventing a newer measurement date."""
import csv
import io
import re
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

GOAL_SOURCE='https://docs.google.com/spreadsheets/d/e/2PACX-1vRsglf4PxOpvzroovCmZGgGQLpUMGd3PEnqqempngNT5zBqPajYbXwoRYVf7r-ekb-dLJ3-oHtgyW35/pub?output=csv'
HEADERS=['現在の再生数','目標','最終更新']

def integer(value):
    value=unicodedata.normalize('NFKC',str(value)).strip().replace(',','')
    if not re.fullmatch(r'\d+',value):raise ValueError('Goal count must be a non-negative integer')
    result=int(value)
    if result>1_000_000_000_000:raise ValueError('Goal count out of range')
    return result

def measured_at(value):
    match=re.fullmatch(r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?',value.strip())
    if not match:raise ValueError('Goal must have an explicit measurement date')
    year,month,day,hour,minute=[int(x or 0) for x in match.groups()]
    return datetime(year,month,day,hour,minute,tzinfo=ZoneInfo('Asia/Tokyo'))

def parse_goal(data,now=None):
    now=now or datetime.now(timezone.utc)
    rows=list(csv.reader(io.StringIO(data.decode('utf-8-sig') if isinstance(data,bytes) else data)))
    if len(rows)!=2 or [x.strip() for x in rows[0]]!=HEADERS or len(rows[1])!=3:raise ValueError('Unexpected goal sheet format')
    current,target=map(integer,rows[1][:2])
    if not target:raise ValueError('Goal target must be positive')
    updated=rows[1][2].strip();measured=measured_at(updated)
    if measured>now:raise ValueError('Goal measurement cannot be in the future')
    return {'current':current,'target':target,'updated':updated,'measured_at':measured.isoformat(),'source':'公開目標シート','source_type':'sheet_snapshot','metric':'総再生回数','is_stale':(now-measured).days>14}
