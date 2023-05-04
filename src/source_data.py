import csv
import json
csv.field_size_limit(100000000)

sql_filepath = 'sql/sql2.csv'

# Read articles from csv into dict
articles_dict = {}
with open(sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        articles_dict[temp_dict['_id']] = temp_dict

sources_dict = {
    'The Federalist':'The Federalist',
    'RT':'Russia Today',
    'Newsmax':'Newsmax',
    'Newsmax - Politics':'Newsmax',
    'Glenn Beck':'Glenn Beck',
}

fields = [
    ('_source.wSpacemeta.audience_visits', 'Audience Visits'),
    ('_source.wSpacemeta.newsguard.score', 'NewsGuard Score'),
    ('_source.wSpacemeta.newsguard.orientation', 'NewsGuard Orientation'),
    ('_source.wSpacemeta.newsguard.rating', 'NewsGuard Rating'),
    ('_source.wSpacemeta.newsguard.topic', 'NewsGuard Topic'),
]



### List of all sources
# sources = []
# for article in articles_dict.keys():
#     source = articles_dict[article]['_source.source']
#     if source not in sources:
#         sources.append(source)
# sources = sorted(sources, reverse=False)
# with open('sources.json', 'w') as outfile:
#     json.dump(sources, outfile, default=str)

# ### Prepare dictionary
# source_stats_dict = {}
# for source in sources_dict.keys():
#     source_stats_dict[sources_dict[source]] = {}
#     for field in fields:
#         source_stats_dict[sources_dict[source]][field[1]] = []

# ### Store the field results for each relevant source
# for article in articles_dict.keys():
#     source = articles_dict[article]['_source.source']
#     if source in sources_dict.keys():
#         source_clean = sources_dict[source]
#         if source_clean in sources_dict.values():
#             for field in fields:
#                 source_stats_dict[source_clean][field[1]].append(articles_dict[article][field[0]])
# # with open('source_stats_dict.json', 'w') as outfile:
# #     json.dump(source_stats_dict, outfile, default=str)

# ### List of all sources and all hyperlinks
# sources_and_links = {}
# for article in articles_dict.keys():
#     source = articles_dict[article]['_source.source']
#     if source not in sources_and_links.keys():
#         sources_and_links[source] = []
#     sources_and_links[source].append(articles_dict[article]['_source.url'])
# sources_and_links = dict(sorted(sources_and_links.items()))
# with open('sources_and_links.json', 'w') as outfile:
#     json.dump(sources_and_links, outfile, default=str)

### List of all sources and metadata
sources_and_metadata = {}
for article in articles_dict.keys():
    source = articles_dict[article]['_source.source']
    if source not in sources_and_metadata.keys():
        sources_and_metadata[source] = {
            'links':[],
            'audience_visits':[],
            'newsguard_score':[],
            'newsguard_orientation':[],
            'newsguard_rating':[],
            'newsguard_topic':[],
            'newsguard_type':[],
            }
    sources_and_metadata[source]['links'].append(articles_dict[article]['_source.url'])
    try:
        sources_and_metadata[source]['audience_visits'].append(int(articles_dict[article]['_source.wSpacemeta.audience_visits']))
    except:
        sources_and_metadata[source]['audience_visits'].append(None)
    try:
        sources_and_metadata[source]['newsguard_score'].append(float(articles_dict[article]['_source.wSpacemeta.newsguard.score']))
    except:
        sources_and_metadata[source]['newsguard_score'].append(None)
    sources_and_metadata[source]['newsguard_orientation'].append(articles_dict[article]['_source.wSpacemeta.newsguard.orientation'])
    sources_and_metadata[source]['newsguard_rating'].append(articles_dict[article]['_source.wSpacemeta.newsguard.rating'])
    sources_and_metadata[source]['newsguard_topic'].append(articles_dict[article]['_source.wSpacemeta.newsguard.topic'])
    sources_and_metadata[source]['newsguard_type'].append(articles_dict[article]['_source.wSpacemeta.newsguard.type'])
sources_and_metadata = dict(sorted(sources_and_metadata.items()))
with open('sources_and_metadata.json', 'w') as outfile:
    json.dump(sources_and_metadata, outfile, default=str)