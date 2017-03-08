from django.contrib import admin
from models import Article, Category, NewsSource

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('news_source', 'created', 'title',)

admin.site.register(Article, ArticleAdmin)

class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name',)

admin.site.register(NewsSource, NewsSourceAdmin)

admin.site.register(Category)

