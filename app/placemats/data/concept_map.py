import logging
from collections import defaultdict
from app.placemats.data.frequency_of_word_occurrences import *

logger = logging.getLogger(__name__)

def concept_map(pmids_to_keywords: dict, keyword_to_pmids: dict, pmid_to_authors: dict, keyword_to_jtitle: dict, keyword_to_authors: dict, author_to_jtitle: dict):
    top_keywords = []
    pmid_list = []
    top_authors = []
    top_journals = []
    ## Determine top N keywords using the function: frequent_keywords
    top_keywords = compute_frequent_keywords(pmids_to_keywords, CUTOFF=40)
    ## get the pmid
    pmid_list = compute_frequent_keywords(keyword_to_pmids, top_keywords, CUTOFF=None)
    top_authors = compute_frequent_keywords(pmid_to_authors, pmid_list, CUTOFF=55)
    top_journals = compute_frequent_keywords(keyword_to_jtitle, top_keywords,CUTOFF=55)

    myDictR =defaultdict()
    myDictL = defaultdict()

    for each_key in top_keywords:
        for key1, value1 in keyword_to_jtitle.items():
            right_side = []
            if key1 == each_key:                  ## construct a key:value dictionary where the keyword is the key and the journal name is the value
                for each_value in value1:
                    if each_value in top_journals:
                        right_side.append(each_value)
                myDictR[key1] = right_side

        for key2, value2 in keyword_to_authors.items():
            left_side = []
            if key2 == each_key:                 ## construct a key:value dictionary where the keyword is the key and the author name is the value
                for each_value in value2:
                    if each_value in top_authors:
                        left_side.append(each_value)
                myDictL[key2] = left_side

    concept_map_data = []
    listL = []
    listR = []
    mylist = []
    author_list = []
    journal_list = []

    for each_key in top_keywords:
        mylist = []
   
        if each_key in myDictL.keys():
            mylist = mylist + [each_key]
            string_l = myDictL[each_key]
            if not string_l:
                listL = []
            else:
                listL = string_l
        mylist = mylist + [string_l]
        # concept_map_data = concept_map_data + [mylist]
        author_list += [mylist]

        mylist = []

        if each_key in myDictR.keys():
            mylist = mylist + [each_key]
            string_r = myDictR[each_key]
            if not string_r:
                listR = []
            else:
                listR = [string_r]
        mylist = mylist + [string_r]
        journal_list += [mylist]
        # concept_map_data = concept_map_data + [mylist]
    concept_map_data = author_list + journal_list

    author_jtitle_data = []
    for key, values in author_to_jtitle.items():
        if key in top_authors:
            temp = []
            my_string = []
            my_string = my_string + [key]
            for each_value in values:
                temp.append(each_value)
            my_string = my_string + [temp]
            author_jtitle_data = author_jtitle_data + [my_string]
    return concept_map_data, author_jtitle_data
