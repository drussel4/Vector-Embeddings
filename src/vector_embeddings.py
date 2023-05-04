import os
import csv
import json
csv.field_size_limit(100000000)
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import model from SentenceTransformer
load_dotenv()
model = os.environ.get('MODEL')
model = SentenceTransformer(os.environ.get('MODEL'))

sql_filepath = 'sql/sql2.csv'
articles_filepath = 'outputs/articles_dict.json'

# Calculate similarity between two vectors
def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

# Read articles from csv into dict
articles_dict = {}
with open(sql_filepath, 'rt', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for article in reader:
        temp_dict = {k: v for k, v in zip(headers, article)}
        articles_dict[temp_dict['_id']] = temp_dict

# One-off cosine() calcs
# comp_id = '1407107239'
# field = '_source.text'
# # override_text = ''
# the_federalist_vector = model.encode([articles_dict['1372248802'][field]])[0]
# comparison_vector = model.encode([articles_dict[comp_id][field]])[0]
# # comparison_vector = model.encode([override_text])[0]
# result = cosine(the_federalist_vector, comparison_vector)
# print(field, '-', result)
# field = '_source.title'
# # override_title = 'EXPOSED: YOUR tax dollars are being used for AI to TRACK YOU'
# the_federalist_vector = model.encode([articles_dict['1372248802'][field]])[0]
# comparison_vector = model.encode([articles_dict[comp_id][field]])[0]
# # comparison_vector = model.encode([override_title])[0]
# result = cosine(the_federalist_vector, comparison_vector)
# print(field, '-', result)
# raise Exception

# # Retrieve articles that are stored in JSON
# with open(articles_filepath, 'w') as outfile:
#     json.dump(articles_dict, outfile, default=str)

# Calculate similarities of article headers and bodies
def calculate_similarities():
    target_article = '1372248802'
    source = 'the federalist'
    source_field = '_source.source'
    author = 'margot cleveland'
    author_fields = ['_source.Author', '_source.authors']
    header_field = '_source.title'
    body_field = '_source.text'
    header_vector = model.encode([articles_dict[target_article][header_field]])[0]
    body_vector = model.encode([articles_dict[target_article][body_field]])[0]
    article_rankings = []
    for ct, article in enumerate(articles_dict.keys()):

        # Calc cosines
        header_similarity = cosine(header_vector, model.encode([articles_dict[article][header_field]])[0])
        body_similarity = cosine(body_vector, model.encode([articles_dict[article][body_field]])[0])

        # Check if source matches
        source_match_bool = False
        if source in articles_dict[article][source_field].lower():
            source_match_bool = True
        elif source in articles_dict[article][body_field].lower():
            source_match_bool = True
        
        # Check if author matches
        author_match_bool = False
        for auth_field in author_fields:
            if isinstance(articles_dict[article][auth_field] , str):
                if author in articles_dict[article][auth_field].lower():
                    author_match_bool = True
                    break
            elif isinstance(articles_dict[article][auth_field] , list):
                if author in ''.join(articles_dict[article][auth_field]).lower():
                    author_match_bool = True
                    break
            if author in articles_dict[article][body_field].lower():
                author_match_bool = True
        
        article_rankings.append({
            'id':article,
            'header':header_similarity,
            'body':body_similarity,
            'source':source_match_bool,
            'author':author_match_bool,
            })
        print('Completed cosine() for {} of {}'.format(ct+1, len(articles_dict.keys())))
    print('Finished calculating similarities for {} articles of {} attempted'.format(len(article_rankings), len(articles_dict.keys())))

    # Dump rankings into JSON file
    with open('output/article_rankings.json', 'w') as outfile:
        json.dump(article_rankings, outfile, default=str)
    
    return article_rankings

# article_rankings = calculate_similarities()

# Reorient list into dictionary, store as JSON
with open('output/article_rankings.json') as jf:
    article_rankings = json.load(jf)
article_rankings_dict = {}
for article in article_rankings:
    article_rankings_dict[article['id']] = {
        'body':article['body'],
        'header':article['header'],
        'source':article['source'],
        'author':article['author'],
    }
with open('output/article_rankings_dict.json', 'w') as outfile:
    json.dump(article_rankings_dict, outfile, default=str)
