from django.contrib import admin
from .models import Article, Category, NewsSource, ScraperResult

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('news_source', 'created', 'title',)

admin.site.register(Article, ArticleAdmin)

class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name',)

admin.site.register(NewsSource, NewsSourceAdmin)

class ScraperResultAdmin(admin.ModelAdmin):
    list_display = ('news_source', 'completed_time', 'success',
                    'added_count', 'error_count', 'total_count')

admin.site.register(ScraperResult, ScraperResultAdmin)
admin.site.register(Category)
