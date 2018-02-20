#!/usr/bin/env python

# Before running:
# import nltk
# nltk.download('punkt')
# nltk.download('wordnet')

import os
import requests
from requests.exceptions import ReadTimeout, ConnectTimeout
from datetime import datetime

import tagnews

API_HOST = os.environ.get('API_HOST', 'http://127.0.0.1:8000')
API_TOKEN = os.environ.get('API_TOKEN', '')
MODEL_INFO = os.environ.get('MODEL_INFO', 'code_all_articles')

class ApiClient(object):
    TIMEOUT_S = 10.0

    def __init__(self, host, token):
        self.host = host
        self.token = token

    def fetch_categories(self):
        url = self.absolute('/api/categories')
        return [article for article in self.url_cursor(url)]

    def set_trained_coding(self, article_id, coding):
        url = self.absolute('/api/articles/{}/trained-coding'.format(article_id))
        return self.put(url, json=coding)

    def url_cursor(self, url, params=None):
        next_url = url
        next_params = params

        while next_url:
            resp = self.get(next_url, next_params)
            resp.raise_for_status()

            data = resp.json()

            print("{} fetching {} {}".format(datetime.now().isoformat(), next_url, next_params))

            for item in data.get('results', []):
                yield item

            next_url = data.get('next')
            next_params = None

    def articles_cursor(self, params={}, limit=None):
        count = 0

        url = ''.join([self.host, '/api/articles'])

        for article in self.url_cursor(url, params=params):
            if limit and count > limit:
                break

            count += 1
            yield article

    def absolute(self, path):
        return ''.join([self.host, path])

    def headers(self):
        return {
            'Authorization': 'Token {}'.format(self.token),
        }

    def get(self, url, params=None, retries=3):
        try:
            return requests.get(url,
                headers=self.headers(),
                params=params,
                timeout=ApiClient.TIMEOUT_S)
        except (ReadTimeout, ConnectTimeout):
            if retries >= 1:
                print("retrying GET {}".format(url))
                return self.get(url, params=params, retries=retries-1)

    def put(self, url, json=None, params=None, retries=3):
        try:
            return requests.put(url,
                headers=self.headers(),
                params=params,
                json=json,
                timeout=ApiClient.TIMEOUT_S)
        except (ReadTimeout, ConnectTimeout):
            if retries >= 1:
                print("retrying PUT {}".format(url))
                return self.put(url, json=json, params=params, retries=retries-1)


class Coder(object):
    MIN_SCORE = 0.01

    def __init__(self, categories=[], model_info='unknown'):
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

coder = Coder(categories=client.fetch_categories(), model_info=MODEL_INFO)

count = 0
for article in client.articles_cursor(params={'page': 3772}):
    coding = coder.code_article(article)
    resp = client.set_trained_coding(article['id'], coding)

    #print("{} - {}".format(article['id'], article['url']))

    if not resp.ok:
        print("ERROR: {}".format(resp.text))

