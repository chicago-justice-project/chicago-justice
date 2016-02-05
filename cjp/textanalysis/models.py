from django.db import models
#from django.db.transaction import commit_on_success
from django.db.transaction import atomic
from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article
import re

# Create your models here.

def getWordList(text):
    text = text.lower()
    words = re.findall('\w+', text)
    return words

def countWords(counts, words):
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts

class Word(models.Model):
    word = models.CharField(max_length=255, null=False, db_index=True, unique=True)

class ArticleWord(models.Model):
    word = models.ForeignKey(Word, null=False, db_index=True)
    article = models.ForeignKey(Article, null=False, db_index=True)
    frequency = models.IntegerField(null=False)
    
    class Meta:
        unique_together = ("word", "article")
        
    @staticmethod
    @atomic
    def processArticle(article):
        
        # get lowercase words in title
        title = article.title
        titleWords = getWordList(title)
        
        # get lowercase words in body
        bodytext = article.bodytext
        bodyWords = getWordList(bodytext)
        
        counts = dict()
        counts = countWords(counts, titleWords)        
        counts = countWords(counts, bodyWords)
        
        # delete if word count already exists for an article.
        # may be rebuilding after an update.
        ArticleWord.objects.filter(article = article).delete()
        
        for textWord, cnt in counts.items():
            try:
                word = Word.objects.get(word=textWord)
            except ObjectDoesNotExist:
                word = Word(word=textWord)
                word.save()
            aw = ArticleWord(word=word, frequency=cnt, article=article)
            aw.save()
