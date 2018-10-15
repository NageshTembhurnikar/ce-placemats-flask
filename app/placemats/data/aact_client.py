import psycopg2
from collections import defaultdict, namedtuple

CONN_STRING = "host='aact-db.ctti-clinicaltrials.org' dbname='aact' user='birdseye' password= 'birdseye123'"
ClinicalInfo = namedtuple('ClinicalInfo', ['nctid_to_title', 'nctid_to_status', 'nctid_to_conditions', 'nctid_to_locations', 'nctid_to_loc_status'])


def connect_aact(query_string, parameters=None):
    conn = psycopg2.connect(CONN_STRING)
    cursor = conn.cursor()
    cursor.execute(query_string, parameters)
    # retrieve the records from the database
    records = cursor.fetchall()
    cursor.close()
    conn.close
    return records


def fetch_clin_info(term):
    search_term = '%' + term.lower() + '%'

    query = str('select nct_id, name FROM interventions WHERE LOWER(interventions.name) LIKE %s')
    records1 = connect_aact(query, (search_term,))
    #print(records1)

    nctid_to_title = defaultdict(set)
    nctid_to_conditions = defaultdict(set)
    nctid_to_locations = defaultdict(set)
    nctid_to_status = defaultdict(set)
    nctid_to_loc_status = defaultdict(set)

    if records1:
        ids = []
        ids = [(r[0]) for r in records1]

        query_string = str(
            'select nct_id, start_date FROM studies WHERE studies.nct_id IN %s ORDER BY start_date DESC NULLS LAST')
        records = connect_aact(query_string, (tuple(ids),))

        ids = [(r[0]) for r in records1]
        ids = ids[:12]
        #print(ids
        query_string = str(
            'select nct_id, brief_title FROM studies WHERE studies.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        #print(records)
        [nctid_to_title[r[0]].append(r[1]) if r[0] in list(nctid_to_title.keys())
         else nctid_to_title.update({r[0]: [r[1]]}) for r in records]

        query_string = str(
            'select nct_id,overall_status  FROM studies WHERE studies.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        #print(records)
        [nctid_to_status[r[0]].append(r[1]) if r[0] in list(nctid_to_status.keys())
         else nctid_to_status.update({r[0]: [r[1]]}) for r in records]


        query_string = str(
            'select name, nct_id conditions FROM conditions WHERE conditions.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        #print(records)
        [nctid_to_conditions[r[0]].append(r[1]) if r[0] in list(nctid_to_conditions.keys())
         else nctid_to_conditions.update({r[0]: [r[1]]}) for r in records]

        query_string = str(
            'select nct_id, name FROM facilities WHERE facilities.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))


        #print(records)
        [nctid_to_locations[r[0]].append(r[1]) if r[0] in list(nctid_to_locations.keys())
         else nctid_to_locations.update({r[0]: [r[1]]}) for r in records]

        query_string = str('select nct_id, status FROM facilities WHERE facilities.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        [nctid_to_loc_status[r[0]].append(r[1]) if r[0] in list(nctid_to_loc_status.keys())
         else nctid_to_loc_status.update({r[0]: [r[1]]}) for r in records]

        return ClinicalInfo(nctid_to_title, nctid_to_status, nctid_to_conditions, nctid_to_locations, nctid_to_loc_status)
    else:
        return None


