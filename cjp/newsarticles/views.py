from newsarticles.models import Article, Category, FEED_NAMES
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.db.models import Q, Max, Min
from django.shortcuts import render_to_response, redirect
from django import forms
from django.template import RequestContext
from datetime import datetime


class ArticleForm(forms.Form):
    showAll = forms.BooleanField(label='Show Non-Crime',
                                 initial=False, required=False)
    feedname = forms.ChoiceField(label='Source',
                                 choices=((('ALL', 'All Feeds'),) + FEED_NAMES),
                                 initial='ALL', required=False)
    startDate = forms.DateField(label='Start Date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)
    endDate = forms.DateField(label='End Date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)
    searchTerms = forms.CharField(label='Search Terms', required=False,
                                  max_length=1024)
    category = forms.ModelMultipleChoiceField(label='Category',
                                              required=False, queryset=Category.objects.all())


def articleList(request):
    form = ArticleForm(request.POST)
    clearSearch = request.POST.get('clearSearch', "False") == "False"
    newSearch = request.POST.get('newSearch', "False") == "True"

    if clearSearch and newSearch and form.is_valid():
        showAll = form.cleaned_data['showAll']
        feedname = form.cleaned_data['feedname']
        startDate = form.cleaned_data['startDate']
        endDate = form.cleaned_data['endDate']
        searchTerms = form.cleaned_data['searchTerms']
        categories = form.cleaned_data['category']
        page = 1

        request.session['article_hasSearch'] = True

    elif clearSearch and request.session.get('article_hasSearch', False):
        request.session['article_hasSearch'] = True

        showAll = request.session['article_showAll']
        feedname = request.session['article_feedname']
        startDate = request.session['article_startDate']
        endDate = request.session['article_endDate']
        searchTerms = request.session['article_searchTerms']
        categories = request.session['article_category']

        form = ArticleForm({
            'showAll' : showAll,
            'feedname' : feedname,
            'startDate' : startDate,
            'endDate' : endDate,
            'searchTerms' : searchTerms,
            'categories' : categories
        })

        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('article_page', 1)

    else:
        form = ArticleForm()

        showAll = False
        feedname = 'ALL'
        startDate = None
        endDate = None
        searchTerms = ''
        categories = []

        # 3/2/2012 John Nicholson
        # added so paging works even when there is no search
        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('article_page', 1)

        request.session['article_hasSearch'] = False

    request.session['article_showAll'] = showAll
    request.session['article_feedname'] = feedname
    request.session['article_startDate'] = startDate
    request.session['article_endDate'] = endDate
    request.session['article_searchTerms'] = searchTerms
    request.session['article_category'] = categories
    request.session['article_page'] = page

    article_list = Article.objects.all().distinct().order_by('-created')
    if not showAll:
        article_list = article_list.filter(relevant=True)
    if feedname != '' and feedname != 'ALL':
        article_list = article_list.filter(feedname=feedname)
    if startDate != None:
        startDate = datetime.strptime("%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__gte=startDate)
    if endDate != None:
        endDate = datetime.strptime("%s 23:59:59" % endDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__lte=endDate)
    if searchTerms:
        article_list = article_list.filter(Q(title__icontains=searchTerms) | Q(bodytext__icontains=searchTerms))
    if categories:
        article_list = article_list.filter(categories__in = categories)

    paginator = Paginator(article_list, 20) # Show 20 articles per page

    try:
        articles = paginator.page(page)
    except (EmptyPage, InvalidPage):
        articles = paginator.page(paginator.num_pages)

    dateRange = Article.objects.all().aggregate(minDate = Min('created'),
                                                maxDate = Max('created'))

    data = {'articles' : articles,
            'form' : form,
            'dateRange' : dateRange,
           }
    return render_to_response('newsarticles/articleList.html', data,
                              context_instance=RequestContext(request))


def articleView(request, articleId, action=None):
    try:
        article = Article.objects.get(id = articleId)
    except:
        article = None

    categories = Category.objects.all().order_by('category_name')

    if action == 'print':
        actionMessage = None
        template = 'newsarticles/printArticle.html'

    elif action == 'relevant' and article and request.user.is_authenticated():
        try:
            article.relevant = not (request.POST['relevant'] == 'True')
            article.save()
        except:
            pass
        actionMessage = "Crime Related has been updated"
        template = 'newsarticles/article.html'

    elif action == 'updateCategories' and article and request.user.is_authenticated():
        article.categories.clear()
        for key, val in request.POST.iteritems():
            if key.startswith('category_'):
                try:
                    category = Category.objects.get(pk=val)
                    article.categories.add(category)
                except:
                    pass
        article.save()
        actionMessage = "Categories have been updated"
        template = 'newsarticles/article.html'

    else:
        actionMessage = None
        template = 'newsarticles/article.html'

    data = {'article' : article,
            'categories' : categories,
            'actionMessage' : actionMessage,
           }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


class CategoryForm(forms.Form):
    category_name = forms.CharField(label='Category Name', required=True, max_length=256)
    abbreviation = forms.CharField(label='Abbreviation', required=True, max_length=5,
                                   widget=forms.TextInput(attrs={'size':'5'}))

    def clean_category_name(self):
        data = self.cleaned_data['category_name']
        data = data.strip()
        if len(data) == 0:
            raise forms.ValidationError("requires at least one character")
        return data

    def clean_abbreviation(self):
        data = self.cleaned_data['abbreviation']
        data = data.strip()
        if len(data) == 0:
            raise forms.ValidationError("requires at least one character")
        return data


def manageCategoryView(request, category_id=None):
    if not (request.user.is_authenticated() and request.user.is_superuser):
        return redirect('/')

    if category_id:
        try:
            category = Category.objects.get(pk=category_id)
            categoryForm = CategoryForm({'category_name' : category.category_name,
                                         'abbreviation' : category.abbreviation})
        except:
            categoryForm = CategoryForm()
            category = None
    else:
        categoryForm = CategoryForm()
        category = None

    if request.POST:
        categoryForm = CategoryForm(request.POST)
        if categoryForm.is_valid():
            cleanData = categoryForm.cleaned_data
            if category:
                category.category_name = cleanData['category_name']
                category.abbreviation = cleanData['abbreviation']
            else:
                category = Category(category_name=cleanData['category_name'],
                                    abbreviation=cleanData['abbreviation'])
            category.save()

            categoryForm = CategoryForm()
            category_id = None

    categories = Category.objects.all().order_by('category_name')
    data = {'categories': categories,
            'categoryForm': categoryForm,
            'category_id' : category_id,
            }
    return render_to_response('newsarticles/manageCategory.html', data,
                              context_instance=RequestContext(request))

class ArticleListBuilderForm(forms.Form):
    feedname = forms.ChoiceField(label='Source',
                                 choices=((('ALL', 'All Feeds'),) + FEED_NAMES),
                                 initial='ALL', required=False)
    startDate = forms.DateField(label='Start Date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)
    endDate = forms.DateField(label='End Date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)

def emailArticleListBuilder(request):
    if not (request.user.is_authenticated() and request.user.is_superuser):
        return redirect('/')

    articleListBuilderForm = ArticleListBuilderForm(request.POST)

    articles = []
    if request.POST and articleListBuilderForm.is_valid():
        didSearch = True
        feedname = articleListBuilderForm.cleaned_data['feedname']
        startDate = articleListBuilderForm.cleaned_data['startDate']
        endDate = articleListBuilderForm.cleaned_data['endDate']

        articles = Article.objects.filter(relevant=True).distinct().order_by('-created')
        if feedname != '' and feedname != 'ALL':
            articles = articles.filter(feedname=feedname)
        if startDate != None:
            startDate = datetime.strptime("%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
            articles = articles.filter(created__gte=startDate)
        if endDate != None:
            endDate = datetime.strptime("%s 23:59:59" % endDate, "%Y-%m-%d %H:%M:%S")
            articles = articles.filter(created__lte=endDate)

        articleCount = articles.count()
        if articleCount > 200:
            tooManyArticles = True
            didSearch = False
            articles = []
        else:
            tooManyArticles = False

    else:
        didSearch = False
        tooManyArticles = False


    dateRange = Article.objects.all().aggregate(minDate = Min('created'),
                                                maxDate = Max('created'))

    data = {'articleListBuilderForm' : articleListBuilderForm,
            'dateRange' : dateRange,
            'articles' : articles,
            'didSearch' : didSearch,
            'tooManyArticles' : tooManyArticles,
            }

    return render_to_response('newsarticles/emailArticleListBuilder.html', data,
                              context_instance=RequestContext(request))

def emailArticleList(request):
    if not (request.user.is_authenticated() and request.user.is_superuser):
        return redirect('/')



    if request.POST:
        articleIds = request.POST.getlist('articleId')
        articles = Article.objects.filter(pk__in=articleIds).order_by('-created')
    else:
        articles = []

    data = {'articles' : articles,
            }

    return render_to_response('newsarticles/emailArticleList.html', data,
                              context_instance=RequestContext(request))



