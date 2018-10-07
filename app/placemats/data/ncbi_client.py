import Bio.Entrez
import Bio.Medline
import logging
import typing
import random
import string
from app.placemats.util import *
from collections import defaultdict, namedtuple

logger = logging.getLogger(__name__)

API_KEY = None

MAX_PER_PAGE = 2000
AUTHOR_NAME = 'AU'
PMID = 'PMID'
ABSTRACT = 'AB'
TITLE = 'TI'
AFFILIATION = 'AD'
DATE_OF_PUBLICATION = 'DP'
TERMS = 'MH'
J_TITLE = 'JT'
AUTHOR_NAME = 'AU'
PUBLICATION_TYPE = 'PT'

def configure_client(email='dev.robot@gmail.com', api_key=None):
    """
    Must be called once before calling any of the other API's

    HACK: when deployed, we wanna assign a unique email to each instance to avoid throttling
    :param email:
    :param api_key:
    """

    if email == 'ncbi.robot.user@gmail.com':
        email = 'ncbi.robot.{}-user@gmail.com'.format(''.join(random.choices(string.ascii_uppercase + string.digits, k=5)))
        logger.info('Setting email to %s', email)
    Bio.Entrez.email = email
    global API_KEY
    API_KEY = api_key


def call(procedure, *args, **kwargs):
    """
    Wraps all our calls to Entrez API's. Acts as our 'http interceptor'.
    :type procedure: function
    :param procedure: Entrez function to invoke
    :param args:
    :param kwargs:
    :return:
    """
    logger.debug('Calling {} with args: {}, kwargs: {}'.format(procedure.__name__, args, kwargs))
    if API_KEY:
        kwargs['api_key'] = API_KEY
    handle = procedure(*args, **kwargs)
    if kwargs.get('rettype') == 'medline':
        out = Bio.Medline.parse(handle)
        out = list(out)
    elif procedure.__name__ == "efetch" and kwargs.get('db') == "mesh" and kwargs.get('rettype') == 'full':
        out = handle.read()
    else:
        out = Bio.Entrez.read(handle)
    handle.close()
    return out


def efetch(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    """
    return call(Bio.Entrez.efetch, *args, **kwargs)


def egquery(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    """
    return call(Bio.Entrez.egquery, *args, **kwargs)


def esearch(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return:
    """
    return call(Bio.Entrez.esearch, *args, **kwargs)

'''
def pubmed_search(term, skip=0, limit=MAX_PER_PAGE, sort='relevance'):
    retmax = min(limit, MAX_PER_PAGE)
    out = esearch(db='pubmed', sort=sort, term=term, retstart=skip, retmax=retmax)
    logger.info('Pubmed search query: %s ; translation-set: %s', term, out['TranslationSet'])
    return out
'''
def pubmed_search(term, pub_type = None, skip=0, limit=MAX_PER_PAGE, sort='relevance'):
    retmax = min(limit, MAX_PER_PAGE)
    search_term = term
    if pub_type == 'research':
        search_term = term + '[ALL] AND (("Journal Article"[PTYP]) OR ("Multicenter Study"[PTYP]) OR ("Editorial"[PTYP]) OR ("Introductory Journal Article"[PTYP]) OR ("News"[PYPT]) OR ("Newspaper Article"[PYPT]) OR ("Review"[PYPT]) OR ("Validation Studies"[PYPT]))'
    if pub_type == 'clinical':
        search_term = term + '[ALL] AND (("Adaptive Clinical Trial"[PTYP]) OR ("Case Reports"[PTYP]) OR ("Clinical Conference"[PTYP]) OR ("Clinical Study"[PTYP]) OR ("Clinical Trial, Phase I"[PTYP]) OR ("Clinical Trial, Phase II"[PTYP]) OR ("Clinical Trial, Phase III"[PTYP]) OR ("Clinical Trial, Phase IV"[PTYP]) OR ("Clinical Trial"[PTYP]) OR ("Comparative Study"[PTYP])  OR ("Controlled Clinical Trial"[PTYP])  OR ("Equivalence Trial"[PTYP]) OR ("Observational Study"[PTYP]) OR ("Pragmatic Clinical Trial"[PTYP]) OR ("Randomized Controlled Trial"[PTYP]) OR ("Twin Study"[PYPT]))'

    out = esearch(db='pubmed', sort=sort, term=search_term, retstart=skip, retmax=retmax)
    logger.info('Pubmed search query: %s ; translation-set: %s', term, out['TranslationSet'])
    return out


def get_medline_infos(ids):
    """
    See https://www.nlm.nih.gov/bsd/mms/medlineelements.html for a description of the medline fields.
    :param ids:
    :return:
    """
    infos = []
    for ids_chunk in chunks(ids, MAX_PER_PAGE):
        infos.extend(efetch(db='pubmed', id=ids_chunk, rettype='medline', retmode='text'))
    return infos


def get_pmids_for_term(term, pub_type, limit):
    pmids = []
    current = pubmed_search(term, pub_type)
    current_id_list = current['IdList']
    while len(pmids) < limit and current_id_list:
        pmids.extend(current_id_list)
        current = pubmed_search(term, pub_type = pub_type, skip=len(pmids))
        current_id_list = current['IdList']
    return pmids[:limit]


AuthorInfo = namedtuple('AuthorInfo', ['pmid_to_authors', 'author_to_pmids', 'pmid_to_articles'])
Article = namedtuple('Article', ['title', 'abstract', 'date_of_publication'])
KeywordInfo = namedtuple('KeywordInfo', ['pmids_to_keywords', 'keyword_to_pmids','pmid_to_articles'])
KeywordInfo2 = namedtuple('KeywordInfo2', ['pmids_to_keywords', 'keyword_to_pmids','pmid_to_authors','keyword_to_jtitle','keyword_to_authors'])

def affiliations(term, pub_type = None, limit=20_000) -> typing.Dict[str, str]:

    medline_infos = get_medline_infos(get_pmids_for_term(term, pub_type, limit))
    out = {}
    for m_info in medline_infos:
        if AFFILIATION not in m_info:
            logger.warning('[affiliations] Affiliation not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        out[m_info[PMID]] = m_info[AFFILIATION]
    return out


def author_info(term, limit=20_000):
    pmids = get_pmids_for_term(term, None, limit)
    pmid_to_authors = defaultdict(set)
    author_to_pmids = defaultdict(set)
    pmid_to_articles = {}
    medline_infos = get_medline_infos(pmids)
    for m_info in medline_infos:
        if AUTHOR_NAME not in m_info:
            logger.warning('[author_info] Author name not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        if PUBLICATION_TYPE not in m_info:
            logger.warning('[author_info] Publication Type name not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue

        pmid = m_info[PMID]
        for name in m_info[AUTHOR_NAME]:
            author_to_pmids[name].add(pmid)
            pmid_to_authors[pmid].add(name)
            publication_year = extract_publication_year(m_info.get(DATE_OF_PUBLICATION))
            pmid_to_articles[pmid] = Article(m_info.get(TITLE), m_info.get(ABSTRACT), publication_year)

    return AuthorInfo(pmid_to_authors, author_to_pmids, pmid_to_articles)


def keyword_info(term, limit=20_000):
    pmids = get_pmids_for_term(term, None, limit)
    pmids_to_keywords = defaultdict(set)
    keyword_to_pmids = defaultdict(set)
    pmid_to_articles = {}
    medline_infos = get_medline_infos(pmids)
    for m_info in medline_infos:
        if TERMS not in m_info:
            logger.warning('[Terms] MeSH Terms not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        pmid = m_info[PMID]
        for each_term in m_info[TERMS]:
            extracted_term = extract_term(each_term)
            keyword_to_pmids[extracted_term].add(pmid)
            pmids_to_keywords[pmid].add(extracted_term)
            publication_year = extract_publication_year(m_info.get(DATE_OF_PUBLICATION))
            pmid_to_articles[pmid] = Article(m_info.get(TITLE), m_info.get(ABSTRACT), publication_year)
    return KeywordInfo(pmids_to_keywords, keyword_to_pmids, pmid_to_articles)

def keyword_info_astericks(term, limit=20_000):
    '''
    same as keyword_info but only for keywords with *
    Used for Visual 7
    :param term:
    :param limit:
    :return:
    '''
    pmids = get_pmids_for_term(term, None, limit)
    pmids_to_keywords = defaultdict(set)
    keyword_to_pmids = defaultdict(set)
    pmid_to_articles = {}
    medline_infos = get_medline_infos(pmids)


    for m_info in medline_infos:
        if TERMS not in m_info:
            logger.warning('[Terms] MeSH Terms not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        pmid = m_info[PMID]
        star = False
        for each_term in m_info[TERMS]:
            if '*' not in each_term:
                continue
            else:
                extracted_term = extract_term(each_term)
                if extracted_term.lower() != term.lower():
                    keyword_to_pmids[extracted_term].add(pmid)
                    pmids_to_keywords[pmid].add(extracted_term)
                    star = True
        if star:
            publication_year = extract_publication_year(m_info.get(DATE_OF_PUBLICATION))
            pmid_to_articles[pmid] = Article(m_info.get(TITLE), m_info.get(ABSTRACT), publication_year)

    return KeywordInfo(pmids_to_keywords, keyword_to_pmids, pmid_to_articles)

def keyword_info2(term, limit=20_000):
    '''
    Used for Visual 5 Concept Maps
    Uses only keywords with *
    :param term:
    :param limit:
    :return:
    '''
    pmids = get_pmids_for_term(term, None, limit)
    pmids_to_keywords = defaultdict(set)
    keyword_to_pmids = defaultdict(set)
    pmid_to_authors = defaultdict(set)
    keyword_to_jtitle = defaultdict(set)
    keyword_to_authors = defaultdict(set)
    medline_infos = get_medline_infos(pmids)

    for m_info in medline_infos:
        if TERMS not in m_info:
            logger.warning('[Terms] MeSH Terms not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        if AUTHOR_NAME not in m_info:
            logger.warning('[Terms] AUTHOR not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        if J_TITLE not in m_info:
            logger.warning('[Terms] Journal title not found for term: %s ; PMID: %s', term, m_info[PMID])
            continue
        pmid = m_info[PMID]

        for each_term in m_info[TERMS]:
            if '*' not in each_term:
                continue
            else:

                extracted_term = extract_term(each_term)
                if extracted_term.lower() != term.lower():
                    keyword_to_pmids[extracted_term].add(pmid)
                    pmids_to_keywords[pmid].add(extracted_term)
                    keyword_to_jtitle[extracted_term].add(m_info[J_TITLE])


                    for each_author in m_info[AUTHOR_NAME][0:2]:
                        keyword_to_authors[extracted_term].add(each_author)
                        pmid_to_authors[pmid].add(each_author)


    return KeywordInfo2(pmids_to_keywords, keyword_to_pmids, pmid_to_authors, keyword_to_jtitle, keyword_to_authors)

def extract_publication_year(date_of_publication):
    year = extract_year_format1(date_of_publication)
    if year is None:
        year = extract_year_format2(date_of_publication)
    return year


def extract_year_format1(date_of_publication):
    try:
        if date_of_publication is not None:
            date_parts = date_of_publication.split()
            if len(date_parts) > 0:
                return int(date_parts[0])
        return None
    except:
        print("Unexpected error")
    return None


def extract_year_format2(date_of_publication):
    try:
        if date_of_publication is not None:
            date_parts = date_of_publication.split("-")
            if len(date_parts) > 0:
                return int(date_parts[0])
        return None
    except:
        print("Unexpected error")
    return None


def extract_term(term_value):
    try:
        if term_value is not None:
            term_value_parts = term_value.split('/')
            return term_value_parts[0].replace('*', '')
    except:
        print("Unable to parse term value")
    return None


##############

def mesh_search(term,sort = "relevance"):
    """
    Connect to MeSH database and search for the exact MeSH Term
    :param term:
    :return:
    """
    term = term
    out = esearch(db='mesh', term=term+"[MESH]", retmax=1_00_000)
    #logger.info('Pubmed search query: %s ; translation-set: %s', term, out['TranslationSet'])
    return out

def get_mesh_info(ids):
    mesh_info = []
    for eachEntry in ids:
         mesh_info = efetch(db='mesh', id=eachEntry, rettype='full', retmode='text')
    return mesh_info


def get_mesh_category(term):
    mesh_ids = []
    mesh_category = set()
    mesh_information = mesh_search(term) # calling function mesh search
    mesh_ids = mesh_information['IdList']
    record = get_mesh_info(mesh_ids)
    mesh_category = extract_category(record)
    return mesh_category



def extract_category(mesh_text):
    lookup = 'Tree Number(s): '
    Category_dict = {'A': 'Anatomy',
                     'B': 'Organisms',
                     'C': 'Diseases',
                     'D': 'Chemicals+Drugs',
                     'E': 'Analytical, Diagnostic + Therapeutic Techniques, and Equipment',
                     'F': 'Psychiatry + Psychology',
                     'G': 'Phenomena + Processes',
                     'H': 'Disciplines + Occupation',
                     'I': 'Antropology, Education, Sociology, and Social Phenomena',
                     'J': 'Technology, Industry, and Agriculture',
                     'K': 'Humanities',
                     'L': 'Information Science',
                     'M': 'Named Groups',
                     'N': 'Health Care',
                     'V': 'Publication Characteristic',
                     'Z': 'Geographics'
                     }
    # This is the character at which All MeSH Categories is found in each record retrieved from MeSH
    idx1 = mesh_text.index(lookup) + len(lookup)
    idx2 = mesh_text.index("\n", idx1)
    tree_numbers = mesh_text[idx1:idx2].split(',')
    category = [Category_dict[each_tree.strip()[:1]] for each_tree in tree_numbers]
    category = set(category)
    category = "/".join(category)
    return category

