from django.contrib import admin
import models
from .models import Article, Category, NewsSource, ScraperResult

@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('news_source', 'created', 'title',)

@admin.register(models.NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name',)

@admin.register(models.ScraperResult)
class ScraperResultAdmin(admin.ModelAdmin):
    list_display = ('news_source', 'completed_time', 'success',
                    'added_count', 'error_count', 'total_count')

admin.site.register(Category)

@admin.register(models.UserCoding)
class UserCodingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'date')