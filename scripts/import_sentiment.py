
from newsarticles.models import Article, UserCoding
from django.contrib.auth.models import User

u = User.objects.get(username='matt')

for line in open("/tmp/sentiment.csv"):
    id, _, sentiment = line.split(",")
    a = Article.objects.get(id=int(id))
    try:
      sentiment = int(float(sentiment))
    except:
      sentiment = None
    if sentiment is not None and sentiment <= 1 and sentiment >= -1:
        uc, created = UserCoding.objects.update_or_create(
            article=a,
            defaults={
                'user': u,
                'relevant': True,
                'sentiment': sentiment,
            }
        )
        print("made UC for id {} - created? {}".format(a.id, created))

