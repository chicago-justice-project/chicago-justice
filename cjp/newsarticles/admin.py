from django.contrib import admin
import newsarticles.models as models

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

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'abbreviation', 'kind', 'active')

@admin.register(models.UserCoding)
class UserCodingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'date')
