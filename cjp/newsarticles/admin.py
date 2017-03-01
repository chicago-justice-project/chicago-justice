from django.contrib import admin
from models import Article, Category, NewsSource

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('feedname', 'created', 'title',)

admin.site.register(Article, ArticleAdmin)

admin.site.register(Category)

