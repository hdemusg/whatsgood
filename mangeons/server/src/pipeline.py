import pandas as pd
import numpy as np
import spacy
import texthero as hero
import chars2vec as c2v
import json
from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier

class Pipeline:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.c2v_model = c2v.load_model("eng_50")
        self.bin_clf = load("random_forest_food_classifier.joblib")
        self.mul_clf = load("model.sav")

    def review_2_noun_phrases(self, text):
      doc = self.nlp(text)

      noun_phrases = [chunk.text for chunk in doc.noun_chunks]
      cleaned_phrases = hero.clean(pd.Series(noun_phrases))
      cleaned_phrases.replace('', np.nan, inplace=True)
      return list(cleaned_phrases.dropna())

    def noun_phrases_2_embeds(self, phrases_list):
      print(phrases_list)
      embeddings = self.c2v_model.vectorize_words(phrases_list)
      return embeddings

    def get_foods(self, noun_phrases, embeddings):
      labels = self.bin_clf.predict(embeddings)
      indices = np.flatnonzero(labels)
      food_noun_phrases = [ noun_phrases[index] for index in indices ]
      return food_noun_phrases

    def get_foods_from_reviews(self, reviews_json):
      list_of_reviews = reviews_json["reviews"]
      processed_reviews_object = {
          "reviews": []
      }

      for review in list_of_reviews:
        noun_phrases = self.review_2_noun_phrases(review["review"])
        embeddings = self.noun_phrases_2_embeds(noun_phrases)
        detected_foods = self.get_foods(noun_phrases, embeddings)

        processed_reviews_object["reviews"].append({
            "menu_items": detected_foods,
            "stars": review["stars"]
        })

      return processed_reviews_object

    def foods_2_summary(self, data_in):

        """data_in = {
            'reviews': [
                {
                    'menu_items': ['beer', 'german chocolate cake', 'sausage platter'],
                    'stars': 4.5
                },
                {
                    'menu_items': ['soda of the day', 'breakfast platter', 'german chocolate cake'],
                    'stars': 3.5
                },
                {
                    'menu_items': ['beer', 'starter kielbasa sausage', 'german chocolate cake'],
                    'stars': 2.0
                }
            ]
        }"""

        for review in data_in['reviews']:
            review['categories'] = {'appetizers': 0, 'entrees': 0, 'sides': 0, 'desserts': 0, 'drinks': 0,
                                    'specials': 0}

            if review['menu_items']:
                print(review['menu_items'])
                embeddings = self.noun_phrases_2_embeds(review['menu_items'])

                preds = self.mul_clf.predict(embeddings)
            else:
                preds = []
            """if review['menu_items'][1] == 'german chocolate cake':
                preds = ['drinks', 'desserts', 'entrees']
            if review['menu_items'][1] == 'breakfast platter':
                preds = ['specials', 'entrees', 'desserts']
            if review['menu_items'][1] == 'starter kielbasa sausage':
                preds = ['drinks', 'appetizers', 'desserts']"""

            review['preds'] = preds
            for pred in preds:
                review['categories'][pred] += 1

        data_out = {
            'categories': {
                'appetizers': {'stars': 0, 'count': 0, 'items': {}},
                'entrees': {'stars': 0, 'count': 0, 'items': {}},
                'sides': {'stars': 0, 'count': 0, 'items': {}},
                'desserts': {'stars': 0, 'count': 0, 'items': {}},
                'drinks': {'stars': 0, 'count': 0, 'items': {
                    'beer': {'stars': 0, 'count': 0}
                }},
                'specials': {'stars': 0, 'count': 0, 'items': {}}
            }
        }
        for review in data_in['reviews']:
            rating = review['stars']

            for cat in review['categories']:
                out_cat = data_out['categories'][cat]
                if review['categories'][cat] > 0:
                    out_cat['stars'] = ((out_cat['stars'] * out_cat['count']) + (
                                rating * review['categories'][cat])) / (out_cat['count'] + review['categories'][cat])
                    out_cat['count'] += review['categories'][cat]

            for i in range(len(review['preds'])):
                menu_item = review['menu_items'][i]
                pred = review['preds'][i]

                dic = data_out['categories'][pred]['items']
                if menu_item not in dic:
                    dic[menu_item] = {'stars': 0, 'count': 0}
                dic[menu_item]['stars'] = ((dic[menu_item]['stars'] * dic[menu_item]['count']) + (rating * 1)) / (
                            dic[menu_item]['count'] + 1)
                dic[menu_item]['count'] += 1

        return data_out

    def process(self, reviews_json):
        foods = self.get_foods_from_reviews(reviews_json)
        summary = self.foods_2_summary(foods)
        return summary