from newsarticles.models import Article, Category, TrainedCoding
from newsarticles.api_serializers import ArticleSerializer, CategorySerializer, TrainedCodingSerializer
from rest_framework import viewsets, routers


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.active().order_by('id')
    serializer_class = CategorySerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('-last_modified')
    serializer_class = ArticleSerializer


class TrainedCodingViewSet(viewsets.ModelViewSet):
    queryset = TrainedCoding.objects.all().order_by('article')
    serializer_class = TrainedCodingSerializer


def router_urls():
    router = routers.DefaultRouter()
    router.register(r'articles', ArticleViewSet)
    router.register(r'categories', CategoryViewSet)
    router.register(r'trained-codings', TrainedCodingViewSet)

    return router.urls
