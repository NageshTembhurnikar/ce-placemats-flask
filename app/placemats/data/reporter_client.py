import requests
import datetime
import logging
from collections import namedtuple

logger = logging.getLogger(__name__)


URL = 'https://api.federalreporter.nih.gov/v1/projects/search?'
LIMIT = '50'
TOTAL_RECORDS = 1000


BudgetInfo = namedtuple('BudgetInfo', ['reporter_info','grant_count'])


def get_response(term, offset_value=1, query_by='keyword'):
    offset = "&offset=" + str(offset_value)
    retrieval_limit = "&limit=" + LIMIT
    if query_by == 'keyword':
        search_query = "query=text:"+term+"$textFields:title,abstract,terms"
    elif query_by == 'investigator':
        search_query = "query=piName:"+term

    response = requests.get(URL+search_query+offset+retrieval_limit)
    logger.debug('Connected to RePORTER with status code: {}, starting offset is {}'.format(response.status_code, offset_value))
    return response.json()


def reporter_search(term):
    term = term
    offset_value = 1
    reporter_info = []

    info = get_response(term, offset_value, query_by='keyword')
    grant_count1 = info['totalCount']
    info = get_response(term, offset_value, query_by='investigator')
    grant_count2 = info['totalCount']

    if grant_count1 > grant_count2:
        query_by = 'keyword'
        grant_count = grant_count1
    elif grant_count2 > grant_count1:
        query_by = 'investigator'
        grant_count = grant_count2


    while True:
        # loop body
        info = get_response(term, offset_value, query_by)
        if (offset_value > grant_count) or (offset_value > TOTAL_RECORDS):
            break
        else:

            reporter_info = reporter_info + info['items']
            offset_value += 50
            # Sort by Total Amount; Descending Order, and missing value

    reporter_info_sorted = sorted(reporter_info, key=lambda k: (k['totalCostAmount'] is None, k['totalCostAmount']), reverse=True)

    return BudgetInfo(reporter_info_sorted, grant_count)


def time_duration(dateStart,dateEnd):
    ## Takes two date  strings in the format  2014-05-31T00:00:00
    ## Calculate the difference between in terms of years
    if not dateStart:
        return None
    elif not dateEnd:
        return None
    else:
        st = datetime.datetime.strptime(dateStart, '%Y-%m-%dT%H:%M:%S')
        et = datetime.datetime.strptime(dateEnd, '%Y-%m-%dT%H:%M:%S')
        duration = et - st
        return(duration.days/365)





