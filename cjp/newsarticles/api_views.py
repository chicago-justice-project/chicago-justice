from newsarticles.models import Article, Category, TrainedCoding
from newsarticles.api_serializers import ArticleSerializer, CategorySerializer, TrainedCodingSerializer
from rest_framework import viewsets, routers
from rest_framework.response import Response
from rest_framework.decorators import detail_route


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.active().order_by('id')
    serializer_class = CategorySerializer


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all().order_by('-last_modified')
    serializer_class = ArticleSerializer

    @detail_route(methods=['put'], url_path='trained-coding')
    def set_trained_coding(self, request, pk=None):
        data = request.data.copy()

        data['article'] = pk
        coding = TrainedCodingSerializer(data=data)

        coding.is_valid(raise_exception=True)
        coding.save()
        return Response({'status': 'saved'})


class TrainedCodingViewSet(viewsets.ModelViewSet):
    queryset = TrainedCoding.objects.all()
    serializer_class = TrainedCodingSerializer


def router_urls():
    router = routers.DefaultRouter(trailing_slash=False)
    router.register(r'articles', ArticleViewSet)
    router.register(r'categories', CategoryViewSet)
    router.register(r'trained-codings', TrainedCodingViewSet)

    return router.urls
