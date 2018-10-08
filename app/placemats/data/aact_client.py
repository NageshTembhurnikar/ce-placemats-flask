import logging
import psycopg2
from collections import defaultdict, namedtuple
logger = logging.getLogger(__name__)
CONN_STRING = "host='aact-db.ctti-clinicaltrials.org' dbname='aact' user='birdseye' password= 'birdseye123'"
ClinicalInfo = namedtuple('ClinicalInfo', ['nctid_to_title','nctid_to_status', 'status_to_nctid', 'nctid_to_conditions'])


def connect_aact(query_string, parameters=None):
    conn = psycopg2.connect(CONN_STRING)
    cursor = conn.cursor()
    cursor.execute(query_string, parameters)
    # retrieve the records from the database
    records = cursor.fetchall()
    cursor.close()
    conn.close
    return records


def fetch_ct_info(term):
    search_term = '%' + term.lower() + '%'

    query = str('SELECT nct_id FROM studies WHERE (LOWER(studies.brief_title) LIKE %s OR LOWER(studies.official_title) LIKE %s) \
    UNION \
    SELECT nct_id from facility_investigators where LOWER(facility_investigators.name) LIKE %s\
    UNION \
    SELECT nct_id from keywords WHERE LOWER(keywords.downcase_name) LIKE %s\
    UNION \
    SELECT nct_id from facilities where LOWER(facilities.name) LIKE %s')
    records1 = connect_aact(query, (search_term, search_term, search_term, search_term, search_term,))

    if records1:
        ids = []
        ids = [(r[0]) for r in records1]

        query_string = str('SELECT nct_id, start_date FROM studies WHERE studies.nct_id IN %s ORDER BY start_date DESC NULLS LAST')
        records = connect_aact(query_string, (tuple(ids),))

        records = records[:55]
        ids = [(r[0]) for r in records]

        nctid_to_title = defaultdict(set)
        nctid_to_conditions = defaultdict(set)
        nctid_to_status = defaultdict(set)
        status_to_nctid = defaultdict(set)

        query_string = str('SELECT nct_id, brief_title FROM studies WHERE studies.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        [nctid_to_title[r[0]].append(r[1]) if r[0] in list(nctid_to_title.keys())
         else nctid_to_title.update({r[0]: [r[1]]}) for r in records]

        query_string = str('SELECT nct_id, overall_status FROM studies WHERE studies.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        [nctid_to_status[r[0]].append(r[1]) if r[0] in list(nctid_to_status.keys())
         else nctid_to_status.update({r[0]: [r[1]]}) for r in records]

        [status_to_nctid[r[1]].append(r[0]) if r[1] in list(status_to_nctid.keys())
         else status_to_nctid.update({r[1]: [r[0]]}) for r in records]

        ## Pull Keywords
        query_string = str('SELECT nct_id,name FROM conditions WHERE conditions.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        [nctid_to_conditions[r[0]].append(r[1]) if r[0] in list(nctid_to_conditions.keys())
         else nctid_to_conditions.update({r[0]: [r[1]]}) for r in records]
        return ClinicalInfo(nctid_to_title, nctid_to_status, status_to_nctid, nctid_to_conditions)
    else:
        return None
