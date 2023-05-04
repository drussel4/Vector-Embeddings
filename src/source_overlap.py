import os
import datetime as dt
import csv
import json
csv.field_size_limit(100000000)
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import pandas as pd

# Import model from SentenceTransformer
load_dotenv()
model = os.environ.get('MODEL')
model = SentenceTransformer(os.environ.get('MODEL'))

fed_sql_filepath = 'sql/sql_thefederalist.csv'
rt_sql_filepath = 'sql/sql_russiatoday.csv'
articles_filepath = 'outputs/articles_dict.json'
cosines_filepath = 'outputs/cosines_dict.json'
cosines_csv = 'outputs/cosines.csv'

### Multiple Body-Fields Check
# Because some articles have null or whitespace (' ') for field '_source.text', we check a few others
# NOTE: We may not want to use '_source.summary' in this analysis since it is AI generated text, not raw content from the source
body_len_min = 20
body_field_preference = ['_source.text', '_source.pretext', '_source.summary']

# Calculate similarity between two vectors
def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

# Read The Federalist articles from csv into dict
the_federalist_dict = {}
with open(fed_sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        the_federalist_dict[temp_dict['_id']] = temp_dict
print('Read in {} The Federalist articles...'.format(len(the_federalist_dict.keys())))

# Read The Federalist articles from csv into dict
russia_today_dict = {}
with open(rt_sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        russia_today_dict[temp_dict['_id']] = temp_dict
print('Read in {} Russia Today articles...'.format(len(russia_today_dict.keys())))

# Calculate cosine similarities of articles published *first* by The Federalist, then after by Russia Today
def cosine_similarities():
    cosines_dict = {}
    all_tries_dict = {}
    all_tries_filepath = 'outputs/all_tries_dict.json'
    counter1 = 0
    hurdle_rates = {
        'possible':0.60,
        'likely':0.75,
        'certain':0.90,
    }
    # body_field = '_source.text'
    for fed_article in the_federalist_dict.keys():
        cosines_dict[fed_article] = {'id':None, 'cosine':None, 'confidence':None, 'field1':None, 'field2':None}
        counter1 += 1
        # if counter1 >= 50:
        #     break
        counter2 = 0

        # Try eligible body-fields
        vector1 = None
        for field1 in body_field_preference:
            if field1 in the_federalist_dict[fed_article].keys():
                body1 = the_federalist_dict[fed_article][field1]
                if body1 is not None and body1.strip() not in ['', ' '] and len(body1) >= body_len_min:
                    vector1 = model.encode([body1])[0]
                    break
        
        # If unable to find a usable body from base article, move on
        if vector1 is None:
            continue

        # Filter to only the comparable articles that were published on or after the base publish date
        fed_created_dt = dt.datetime.strptime(the_federalist_dict[fed_article]['_source.created'][:12].strip(), '%b %d, %Y').date()
        rt_filtered_ids = [x['_id'] for x in russia_today_dict.values() if dt.datetime.strptime(x['_source.created'][:12].strip(),'%b %d, %Y').date() >= fed_created_dt]
        # print('{} articles were published on or after {}...'.format(len(rt_filtered_ids), fed_created_dt))

        # Loop through articles and measure vector similarity
        all_tries_dict[fed_article] = []
        for rt_id in rt_filtered_ids:
            rt_created_dt = dt.datetime.strptime(russia_today_dict[rt_id]['_source.created'][:12].strip(), '%b %d, %Y').date()
            if rt_created_dt >= fed_created_dt:
                # print('Starting {}/{} comparison articles...'.format(counter2+1, len(russia_today_dict.keys())))
                counter2 += 1
                # if counter2 >= 25:
                #     break

                # Try eligible body-fields
                vector2 = None
                for field2 in body_field_preference:
                    if field2 in russia_today_dict[rt_id].keys():
                        body2 = russia_today_dict[rt_id][field2]
                        if body2 is not None and body2.strip() not in ['', ' '] and len(body2) >= body_len_min:
                            vector2 = model.encode([body2])[0]
                            break
                
                # If unable to find a usable body from comparison article, move on
                if vector2 is None:
                    continue
                
                body_similarity = cosine(vector1, vector2)
                if body_similarity >= hurdle_rates['certain']:
                    confidence_level = 'certain'
                elif body_similarity >= hurdle_rates['likely']:
                    confidence_level = 'likely'
                elif body_similarity >= hurdle_rates['possible']:
                    confidence_level = 'possible'
                else:
                    confidence_level = None
                all_tries_dict[fed_article].append({'id':rt_id, 'cosine':body_similarity, 'confidence':confidence_level, 'field1':field1, 'field2':field2})

                # If cosine is None or lower than previous, keep processing
                if cosines_dict[fed_article]['cosine'] is not None:
                    if body_similarity <= cosines_dict[fed_article]['cosine']:
                        continue
                
                # If cosine is higher, update confidence
                if body_similarity >= hurdle_rates['certain']:
                    cosines_dict[fed_article] = {'id':rt_id, 'cosine':body_similarity, 'confidence':'certain', 'field1':field1, 'field2':field2}
                    break
                elif body_similarity >= hurdle_rates['likely']:
                    cosines_dict[fed_article] = {'id':rt_id, 'cosine':body_similarity, 'confidence':'likely', 'field1':field1, 'field2':field2}
                elif body_similarity >= hurdle_rates['possible']:
                    cosines_dict[fed_article] = {'id':rt_id, 'cosine':body_similarity, 'confidence':'possible', 'field1':field1, 'field2':field2}
                
        print('Through {}/{} base articles...'.format(counter1, len(the_federalist_dict.keys())))

    # Write cosine results to JSON
    with open(cosines_filepath, 'w') as outfile:
        json.dump(cosines_dict, outfile, default=str)
    with open(all_tries_filepath, 'w') as outfile:
        json.dump(all_tries_dict, outfile, default=str)
    
    return cosines_dict

# cosines_dict = cosine_similarities()

# # Write dictionary to DataFrame, then to csv
# df = pd.DataFrame.from_dict(cosines_dict, orient='index')
# df.to_csv(cosines_csv, sep=',')
