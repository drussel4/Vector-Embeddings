import csv
import json
csv.field_size_limit(100000000)

# sql_filepath = 'sql/sql2.csv'
# sql_filepath = 'sql/sql_thefederalist.csv'
sql_filepath = 'sql/sql_russiatoday.csv'
article_peakmetrics_id = '1401545673'
article_json_filepath = 'articles/article_{}.json'.format(article_peakmetrics_id)

# Read articles from csv into dict
articles_dict = {}
with open(sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        articles_dict[temp_dict['_id']] = temp_dict

# Write article to JSON
if article_peakmetrics_id in articles_dict.keys():
    with open(article_json_filepath, 'w') as outfile:
        json.dump(articles_dict[article_peakmetrics_id], outfile, default=str)
    print('Found article with key "{}" and created JSON'.format(article_peakmetrics_id))
else:
    print('No sign of key "{}" in dictionary...'.format(article_peakmetrics_id))
