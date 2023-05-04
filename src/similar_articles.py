import csv
import json
csv.field_size_limit(100000000)
cell_max_char = 10000 # Excel enforced max is 32767
import datetime as dt
import re
import pandas as pd

sql_filepath = 'sql/sql2.csv'
article_rankings_filepath = 'outputs/article_rankings_dict.json'
similar_articles_metadata_json = 'outputs/similar_articles_metadata.json'
similar_articles_metadata_csv = 'outputs/similar_articles_metadata.csv'
hurdle_rate = 0.50

# Read articles from csv into dict
articles_dict = {}
with open(sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        articles_dict[temp_dict['_id']] = temp_dict

# Import similarity scores, which were calculated on article title and body
with open(article_rankings_filepath) as jf:
    article_rankings_dict = json.load(jf)

# List of all sources and metadata
similar_articles_metadata = {}
articles_counter = {'header':0, 'body':0, 'both':0, 'neither':0}
keywords = ['peakmetrics', 'newsguard', 'censorshipindustrialcomplex', 'censorship']
for article in articles_dict.keys():

    # Check if article is similar enough to include (either header or body surpass hurdle rate)
    created_dt = dt.datetime.strptime(articles_dict[article]['_source.created'][:12].strip(), '%b %d, %Y').date().strftime('%m/%d/%Y')
    if float(article_rankings_dict[article]['header']) < hurdle_rate and float(article_rankings_dict[article]['body']) < hurdle_rate:
        articles_counter['neither'] += 1
        continue
    elif float(article_rankings_dict[article]['header']) >= hurdle_rate and float(article_rankings_dict[article]['body']) >= hurdle_rate:
        articles_counter['both'] += 1
    elif float(article_rankings_dict[article]['header']) >= hurdle_rate:
        articles_counter['header'] += 1
    elif float(article_rankings_dict[article]['body']) >= hurdle_rate:
        articles_counter['body'] += 1
    
    # Store articles that surpassed either header or body hurdle rate
    source = articles_dict[article]['_source.source']
    if source not in similar_articles_metadata.keys():
        similar_articles_metadata[source] = {
            'article':[],
            'audience_visits':[],
            'newsguard_score':[],
            'newsguard_orientation':[],
            'newsguard_rating':[],
            'newsguard_topic':[],
            'newsguard_type':[],
            }
    title_cleaned =  re.sub('[^A-Za-z0-9]+', '', articles_dict[article]['_source.title']).lower()
    body_cleaned =  re.sub('[^A-Za-z0-9]+', '', articles_dict[article]['_source.text']).lower()
    kw_matches = []
    for kw in keywords:
        if kw in title_cleaned or kw in body_cleaned:
            kw_matches.append(kw)
    similar_articles_metadata[source]['article'].append({
        'id':articles_dict[article]['_id'],
        'url':articles_dict[article]['_source.url'],
        'keywords':kw_matches,
        'created':dt.datetime.strptime(articles_dict[article]['_source.created'][:12].strip(), '%b %d, %Y').date().strftime('%m/%d/%Y'),
        'title':articles_dict[article]['_source.title'],
        'body':articles_dict[article]['_source.text'],
        'similarity':{
            'hurdle': hurdle_rate,
            'title':float(article_rankings_dict[article]['header']),
            'body':float(article_rankings_dict[article]['body']),
            }
    })
    try:
        similar_articles_metadata[source]['audience_visits'].append(int(articles_dict[article]['_source.wSpacemeta.audience_visits']))
    except:
        similar_articles_metadata[source]['audience_visits'].append(None)
    try:
        similar_articles_metadata[source]['newsguard_score'].append(float(articles_dict[article]['_source.wSpacemeta.newsguard.score']))
    except:
        similar_articles_metadata[source]['newsguard_score'].append(None)
    similar_articles_metadata[source]['newsguard_orientation'].append(articles_dict[article]['_source.wSpacemeta.newsguard.orientation'])
    similar_articles_metadata[source]['newsguard_rating'].append(articles_dict[article]['_source.wSpacemeta.newsguard.rating'])
    similar_articles_metadata[source]['newsguard_topic'].append(articles_dict[article]['_source.wSpacemeta.newsguard.topic'])
    similar_articles_metadata[source]['newsguard_type'].append(articles_dict[article]['_source.wSpacemeta.newsguard.type'])

# Summarize findings
print('''
Found {} articles passing the hurdle rate ({}) and rejected {}.
Of those passing, {} passed on both header and body, {} on header, and {} on body.
'''.format(
    articles_counter['both'] + articles_counter['header'] + articles_counter['body'],
    hurdle_rate,
    articles_counter['neither'],
    articles_counter['both'],
    articles_counter['header'],
    articles_counter['body'],
    )
)
'''
Found 63 articles passing the hurdle rate (0.5) and rejected 2677.
Of those passing, 6 passed on both header and body, 37 on header, and 20 on body.
'''

# Aggregate scores, then drop score lists
for source in similar_articles_metadata.keys():
    similar_articles_metadata[source]['stats'] = {
        'matched_articles_ct':len(similar_articles_metadata[source]['article']),
        'audience_visits':None,
        'newsguard_score':None,
        'newsguard_orientation':None,
        'newsguard_rating':None,
        'newsguard_topic':None,
        'newsguard_type':None,
        }
    for field in ['audience_visits', 'newsguard_score']:
        field_list = [i for i in similar_articles_metadata[source][field] if i is not None]
        if len(field_list) > 0:
            similar_articles_metadata[source]['stats'][field] = sum(field_list) / len(field_list)
    for field in ['newsguard_orientation', 'newsguard_rating', 'newsguard_topic', 'newsguard_type']:
        if similar_articles_metadata[source][field][0] not in [None, ' ', 'N/A']:
            similar_articles_metadata[source]['stats'][field] = similar_articles_metadata[source][field][0]
for source in similar_articles_metadata.keys():
    for field in ['audience_visits', 'newsguard_score', 'newsguard_orientation', 'newsguard_rating', 'newsguard_topic', 'newsguard_type']:
        # print('About to delete source "{}" and field "{}"'.format(source, field))
        del similar_articles_metadata[source][field]

# Sort dictionary by source name
similar_articles_metadata = dict(sorted(similar_articles_metadata.items()))

# Write dict to JSON
with open(similar_articles_metadata_json, 'w') as outfile:
    json.dump(similar_articles_metadata, outfile, default=str)

# Flatten dict for writing to csv
indexer = 0
csv_dict = {}
for source in similar_articles_metadata.keys():
    for article in similar_articles_metadata[source]['article']:
        csv_dict[indexer] = {
            'source':source,
            'matched_articles_ct':similar_articles_metadata[source]['stats']['matched_articles_ct'],
            'audience_visits':similar_articles_metadata[source]['stats']['audience_visits'],
            'newsguard_score':similar_articles_metadata[source]['stats']['newsguard_score'],
            'newsguard_orientation':similar_articles_metadata[source]['stats']['newsguard_orientation'],
            'newsguard_rating':similar_articles_metadata[source]['stats']['newsguard_rating'],
            'newsguard_topic':similar_articles_metadata[source]['stats']['newsguard_topic'],
            'newsguard_type':similar_articles_metadata[source]['stats']['newsguard_type'],
            'id':article['id'],
            'url':article['url'],
            'keywords':article['keywords'],
            'created':article['created'],
            'title':article['title'].strip(),
            'body':article['body'].strip()[:cell_max_char],
            'hurdle':article['similarity']['hurdle'],
            'title_similarity':article['similarity']['title'],
            'body_similarity':article['similarity']['body'],
        }
        indexer += 1
print('indexer:', indexer)

# Write dictionary to DataFrame, then to csv
df = pd.DataFrame.from_dict(csv_dict, orient='index')
df.to_csv(similar_articles_metadata_csv, sep=',')
