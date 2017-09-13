from newsarticles.models import Article, Category, TrainedCoding, TrainedCategoryRelevance
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'abbreviation', 'kind', 'created')


class TrainedCategoryRelevanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainedCategoryRelevance
        fields = ('category', 'relevance')


class TrainedCodingSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    categories = TrainedCategoryRelevanceSerializer(many=True)

    class Meta:
        model = TrainedCoding
        fields = ('categories', 'model_info', 'relevance', 'article')

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        coding = TrainedCoding.objects.create(**validated_data)

        for category_data in categories_data:
            TrainedCategoryRelevance.objects.create(coding=coding, **categories_data)

        return coding


class ArticleSerializer(serializers.ModelSerializer):
    news_source = serializers.SlugRelatedField(read_only=True, slug_field='short_name')
    trained_coding = TrainedCodingSerializer

    class Meta:
        model = Article
        fields = ('id', 'title', 'author', 'bodytext', 'url', 'news_source', 'created', 'last_modified')

