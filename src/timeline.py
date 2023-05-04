import csv
import json
csv.field_size_limit(100000000)
import datetime as dt

sql_filepath = 'sql/sql2.csv'
article_rankings_filepath = 'outputs/article_rankings_dict.json'
hurdle_rate = 0.60

# Read articles from csv into dict
articles_dict = {}
with open(sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        articles_dict[temp_dict['_id']] = temp_dict

with open(article_rankings_filepath) as jf:
    article_rankings_dict = json.load(jf)

# article_rankings_dict = sorted(article_rankings_dict, key=lambda k: (-k['body'], -k['header']))
# article_rankings_dict2 = sorted(article_rankings_dict, key=lambda k: (-float(article_rankings_dict[k]['body']), -float(article_rankings_dict[k]['header'])))
# article_rankings_dict2 = sorted(article_rankings_dict.items(), key=lambda k: (-float(article_rankings_dict[k]['body']), -float(article_rankings_dict[k]['header'])))
# with open('article_rankings_dict2.json', 'w') as outfile:
#     json.dump(article_rankings_dict2, outfile, default=str)

# Construct dictionary for the timeline
timeline_dict = {}
for article in articles_dict.keys():
    created_dt = dt.datetime.strptime(articles_dict[article]['_source.created'][:12].strip(), '%b %d, %Y').date().strftime('%m/%d/%Y')
    if created_dt not in timeline_dict.keys():
        timeline_dict[created_dt] = {'matches':0, 'total':0}
    # if article_rankings_dict[article]['source'] is True:
    #     hurdle_rate -= 0.20
    # if article_rankings_dict[article]['author'] is True:
    #     hurdle_rate -= 0.20
    
    # Check if either header or body surpass hurdle rate
    if float(article_rankings_dict[article]['header']) >= hurdle_rate or float(article_rankings_dict[article]['body']) >= hurdle_rate:
        timeline_dict[created_dt]['matches'] += 1
    timeline_dict[created_dt]['total'] += 1

# with open('timeline_dict.json', 'w') as outfile:
#     json.dump(timeline_dict, outfile, default=str)

for date in timeline_dict.keys():
    print('{}|{}|{}'.format(date, timeline_dict[date]['total'], timeline_dict[date]['matches']))