import logging
import psycopg2
from collections import defaultdict, namedtuple
import datetime
CONN_STRING = "host='aact-db.ctti-clinicaltrials.org' dbname='aact' user='birdseye' password= 'birdseye123'"
ClinicalInfo = namedtuple('ClinicalInfo', ['nctid_to_title', 'nctid_to_status', 'nctid_to_conditions', 'nctid_to_phase', 'nctid_to_enrollment','nctid_to_start','nctid_to_end','nctid_to_sponsors'])

logger = logging.getLogger(__name__)
def connect_aact(query_string, parameters=None):
    conn = psycopg2.connect(CONN_STRING)
    cursor = conn.cursor()
    cursor.execute(query_string, parameters)
    # retrieve the records from the database
    records = cursor.fetchall()
    cursor.close()
    conn.close
    return records

def convert_date_to_string(datetime_date):
    if datetime_date:
        return(datetime_date.strftime('%m/%d/%Y'))
    else:
        return None

def fetch_clin_info(term):

    search_term = term.lower()
    search_term = '%'+search_term+'%'

    #query = str('select DISTINCT study_type FROM studies')
    #records1 = connect_aact(query, (search_term,))


    query = str('select nct_id, name FROM interventions WHERE LOWER(interventions.name) LIKE %s')
    records_drugs = connect_aact(query, (search_term,))

    query = str('select nct_id, downcase_name FROM conditions WHERE LOWER(conditions.downcase_name) LIKE %s')
    records_disease = connect_aact(query, (search_term,))

    if records_drugs and not records_disease:
        root_type = 'drug'
        records1 = records_drugs
    elif not records_drugs and records_disease:
        root_type = 'disease'
        records1 = records_disease
    if not records_drugs and not records_disease:
        root_type = ''
        records1 = records_disease
    else:
        ids1 = [(r[0]) for r in records_drugs]
        ids2 = [(r[0]) for r in records_disease]
        if len(ids1) > len(ids2):
            root_type = 'drug'
            records1 = records_drugs
        else:
            root_type = 'disease'
            records1 = records_disease

    logger.info('search query: %s is of type: %s', term, root_type)
    nctid_to_title = defaultdict(set)
    nctid_to_conditions = defaultdict(set)
    nctid_to_sponsor = defaultdict(set)
    nctid_to_status = defaultdict(set)
    nctid_to_enrollment = defaultdict(set)
    nctid_to_phase = defaultdict(set)
    nctid_to_start = defaultdict(set)
    nctid_to_end = defaultdict(set)

    if records1:
        ids = []
        ids = [(r[0]) for r in records1]


        query_string = str('select nct_id, start_date FROM studies WHERE studies.nct_id IN %s ORDER BY start_date DESC NULLS LAST')
        records = connect_aact(query_string, (tuple(ids),))

        ids = [(r[0]) for r in records]
        ids = ids[:500]
        query_string = str('select nct_id,official_title, overall_status, phase, enrollment, start_date, completion_date  FROM studies WHERE studies.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))

        for r in records:
            nctid_to_title[r[0]] = r[1]
            nctid_to_status[r[0]] = r[2]
            nctid_to_phase[r[0]] = r[3]
            nctid_to_enrollment[r[0]] = r[4]
            nctid_to_start[r[0]] = r[5]
            nctid_to_end[r[0]] = r[6]
            #nctid_to_start[r[0]] = convert_date_to_string(r[5])
            #nctid_to_end[r[0]] = convert_date_to_string(r[6])

        if root_type == 'drug':
            query_string = str('select name, nct_id conditions FROM conditions WHERE conditions.nct_id IN %s')
            blank_text = 'Disease Condition\'s Unknown'

        elif root_type == 'disease':
            query_string = str('select name, nct_id conditions FROM interventions WHERE interventions.nct_id IN %s')
            blank_text = 'Intervention\'s Unknown'
        records = connect_aact(query_string, (tuple(ids),))
        print(records)
        if not records:
            for each_id in ids:
                nctid_to_conditions[blank_text].add(each_id)
        else:
            [nctid_to_conditions[r[0]].append(r[1]) if r[0] in list(nctid_to_conditions.keys())
             else nctid_to_conditions.update({r[0]: [r[1]]}) for r in records]
        query_string = str('select nct_id,name FROM sponsors WHERE sponsors.nct_id IN %s')
        records = connect_aact(query_string, (tuple(ids),))
        [nctid_to_sponsor[r[0]].append(r[1]) if r[0] in list(nctid_to_sponsor.keys())
         else nctid_to_sponsor.update({r[0]: [r[1]]}) for r in records]

        return ClinicalInfo(nctid_to_title, nctid_to_status, nctid_to_conditions, nctid_to_phase, nctid_to_enrollment, nctid_to_start, nctid_to_end, nctid_to_sponsor)
    else:
        return None

