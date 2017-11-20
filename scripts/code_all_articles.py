#!/usr/bin/env python

#pip install scipy

# should we include all categories or just above a threshold relevance?
# import nltk
# nltk.download('punkt')
# nltk.download('wordnet')

import os
import requests

import tagnews

API_HOST = os.environ.get('API_HOST', 'http://127.0.0.1:8000')
API_TOKEN = os.environ.get('API_TOKEN', '')

class ApiClient(object):
    TIMEOUT_S = 2.0

    def __init__(self, host, token):
        self.host = host
        self.token = token

    def fetch_categories(self):
        url = ''.join([self.host, '/api/categories'])

        return [article for article in self.url_cursor(url)]

    def url_cursor(self, url, params=None):
        resp = self.get(url, params)
        resp.raise_for_status()

        data = resp.json()

        for item in data.get('results', []):
            yield item

        next_url = data.get('next')
        if next_url:
            yield from self.url_cursor(next_url)


    def articles_cursor(self, params={}, limit=100):
        count = 0

        url = ''.join([self.host, '/api/articles'])

        for article in self.url_cursor(url, params=params):
            if count > limit:
                break

            count += 1
            yield article

    def headers(self):
        return {
            'Authorization': 'Token {}'.format(self.token),
        }

    def get(self, url, params=None):
        return requests.get(url,
            headers=self.headers(),
            params=params,
            timeout=ApiClient.TIMEOUT_S)

    def put(self, url, params=None):
        return requests.put(url,
            headers=self.headers(),
            params=params,
            timeout=ApiClient.TIMEOUT_S)


class Coder(object):
    MIN_SCORE = 0.01

    def __init__(self, categories=[], model_info='Test run 1'):
        self.tagger = tagnews.Tagger()
        self.categories = {cat['abbreviation']: cat['id'] for cat in categories}
        self.model_info = model_info

    def category_value(self, abbreviation, score):
        cat_id = self.categories.get(abbreviation)

        if not cat_id or score < self.MIN_SCORE:
            return None

        return {
            'category': cat_id,
            'relevance': score,
        }

    def code_article(self, article):
        text = article['bodytext']
        probs = self.tagger.tagtext_proba(text)

        cat_values = []
        max_score = 0

        for abbr, score in zip(probs.index, probs.values):
            entry = self.category_value(abbr, score)
            if entry:
                cat_values.append(entry)
                max_score = max(score, max_score)

        coding = {
            'model_info': self.model_info,
            'relevance': max_score,
            'categories': cat_values,
        }

        return coding


client = ApiClient(API_HOST, API_TOKEN)

coder = Coder(categories=client.fetch_categories())

for article in client.articles_cursor(limit=5):
    print(article.get('title'))
    print(coder.code_article(article))

