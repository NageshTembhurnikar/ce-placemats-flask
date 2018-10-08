import logging
from app.placemats.data.frequency_of_word_occurrences import *
logger = logging.getLogger(__name__)

def concept_map2(nctid_to_title: dict, status_to_nctid:dict, nctid_to_conditions:dict):
    top_keywords = compute_frequent_keywords(nctid_to_conditions, CUTOFF=55)

    concept_map2_data = []
    for key, value in status_to_nctid.items():
        mylist = []
        mylist = mylist + [key]
        list_r = []
        for each_value in value:
            list_r.extend(nctid_to_title[each_value])

        mylist = mylist + [list_r]
        concept_map2_data = concept_map2_data + [mylist]

        mylist = []
        mylist = mylist + [key]
        list_l = []
        for each_value in value:
            list_to_add = list(set(nctid_to_conditions[each_value]).intersection(set(top_keywords)))
            for each_l in list_to_add:
                if each_l in list_l:
                    continue
                list_l.append(each_l)
        mylist = mylist + [list_l]
        concept_map2_data = concept_map2_data + [mylist]

    return concept_map2_data
