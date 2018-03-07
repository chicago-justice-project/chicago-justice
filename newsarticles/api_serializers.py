from newsarticles.models import Article, Category, TrainedCoding, TrainedCategoryRelevance
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'abbreviation', 'kind', 'created')


class TrainedCategoryRelevanceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects)

    class Meta:
        model = TrainedCategoryRelevance
        fields = ('category', 'relevance')


class TrainedCodingSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects)
    categories = TrainedCategoryRelevanceSerializer(many=True)

    class Meta:
        model = TrainedCoding
        fields = ('categories', 'model_info', 'relevance', 'article')

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        article = validated_data.pop('article')

        coding, exists = TrainedCoding.objects.update_or_create(
            defaults=validated_data,
            article=article
        )

        TrainedCategoryRelevance.objects.filter(coding=coding.id).delete()
        for category_data in categories_data:
            TrainedCategoryRelevance.objects.create(coding=coding, **category_data)

        return coding


class ArticleSerializer(serializers.ModelSerializer):
    news_source = serializers.SlugRelatedField(read_only=True, slug_field='short_name')
    trained_coding = TrainedCodingSerializer

    class Meta:
        model = Article
        fields = ('id', 'title', 'author', 'bodytext', 'url', 'news_source', 'created', 'last_modified')

