import logging
from collections import Counter
from geotext import GeoText
from iso3166 import countries
from collections import namedtuple

logger = logging.getLogger(__name__)

CountryInfo = namedtuple('CountryInfo', ['country_counts', 'code_to_country'])


def get_country_counts(strings):
    country_counts = Counter()
    for s in strings:
        logger.info('%s', s)
        mentions = GeoText(s).country_mentions
        for country in mentions:
            country_counts[country] += 1  # bump per string; ignore freq. of mentions within one string
    code_to_country = {}
    keys_to_pop = []
    for k in country_counts:
        try:
            code_to_country[k] = countries.get(k)
        except Exception:
            keys_to_pop.append(k)
    for k in keys_to_pop:
        country_counts.pop(k, None)

    country_stats = []
    for code in country_counts:
        country_stats.append({'id': code_to_country[code].alpha3, 'name': code_to_country[code].name, 'articles': country_counts[code]})
    return country_stats
