import json
import random
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q, Max, Min
from django.shortcuts import render, get_object_or_404
from django import forms
from newsarticles.models import Article, Category, NewsSource, UserCoding, SENTIMENT_CHOICES, RACE_CHOICES, ETHNICITY_CHOICES, SEX_CHOICES, WEAP_CHOICES
from newsarticles.forms import GroupedMultModelChoiceField


class ArticleSearchForm(forms.Form):
    showAll = forms.BooleanField(label='Include User-Coded Articles Identified as Non-Crime Related',
                                 initial=False, required=False)

    news_source = forms.ModelMultipleChoiceField(label='News Source',
                                         required=False,
                                         widget=forms.SelectMultiple(attrs={'class':'form-control', 'size':'10'}),
                                         queryset=NewsSource.objects.all())

    startDate = forms.DateField(label='Start Date',
                                widget=forms.DateInput(format="%m/%d/%Y", attrs={'class':'form-control'}),
                                required=False)

    endDate = forms.DateField(label='End Date',
                              widget=forms.DateInput(format="%m/%d/%Y", attrs={'class':'form-control'}),
                              required=False)

    searchTerms = forms.CharField(label='Search Terms', required=False,
                                  max_length=1024,
                                  widget=forms.TextInput(attrs={'class':'form-control'}))

    category = GroupedMultModelChoiceField(label='Categories',
                                           required=False,
                                           queryset=Category.objects.active(),
                                           group_by_field='kind',
                                           group_label=Category.KINDS.get,
                                           widget=forms.SelectMultiple(attrs={'class':'form-control', 'size':'10'}))

    trainedRelevance = forms.DecimalField(label='Overall Trained Relevance (0–1)',
                                          required=False,
                                          max_value=1,
                                          min_value=0,
                                          decimal_places=2,
                                          widget=forms.NumberInput(attrs={'class':'form-control'}))

    categoryRelevance = forms.DecimalField(label='Category Trained Relevance (0–1)',
                                           required=False,
                                           max_value=1,
                                           min_value=0,
                                           decimal_places=2,
                                           widget=forms.NumberInput(attrs={'class':'form-control'}))

def articleList(request):
    form = ArticleSearchForm(request.POST)
    # TODO: put these into the form itself
    clearSearch = request.POST.get('clearSearch', "False") == "False"
    newSearch = request.POST.get('newSearch', "False") == "True"

    if clearSearch and newSearch and form.is_valid():
        showAll = form.cleaned_data['showAll']
        news_source = form.cleaned_data['news_source']
        startDate = form.cleaned_data['startDate']
        endDate = form.cleaned_data['endDate']
        searchTerms = form.cleaned_data['searchTerms']
        categories = form.cleaned_data['category']
        trainedRelevance = form.cleaned_data['trainedRelevance']
        categoryRelevance = form.cleaned_data['categoryRelevance']
        page = 1

        request.session['article_hasSearch'] = True

    elif clearSearch and request.session.get('article_hasSearch', False):
        request.session['article_hasSearch'] = True

        showAll = request.session['article_showAll']
        news_source = request.session['article_news_source']
        startDate = request.session['article_startDate']
        endDate = request.session['article_endDate']
        searchTerms = request.session['article_searchTerms']
        categories = request.session['article_category']
        trainedRelevance = request.session['article_trainedRelevance']
        categoryRelevance = request.session['article_categoryRelevance']

        form = ArticleSearchForm({
            'showAll': showAll,
            'news_source': news_source,
            'startDate': startDate,
            'endDate': endDate,
            'searchTerms': searchTerms,
            'categories': categories,
            'trainedRelevance': trainedRelevance,
            'categoryRelevance': categoryRelevance
        })

        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('article_page', 1)

    else:
        form = ArticleSearchForm()

        showAll = False
        news_source = []
        startDate = None
        endDate = None
        searchTerms = ''
        categories = []
        trainedRelevance = None
        categoryRelevance = None

        # added so paging works even when there is no search
        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('article_page', 1)

        request.session['article_hasSearch'] = False

    request.session['article_showAll'] = showAll
    request.session['article_news_source'] = news_source
    request.session['article_startDate'] = startDate
    request.session['article_endDate'] = endDate
    request.session['article_searchTerms'] = searchTerms
    request.session['article_category'] = categories
    request.session['article_page'] = page
    request.session['article_trainedRelevance'] = trainedRelevance
    request.session['article_categoryRelevance'] = categoryRelevance

    article_list = Article.objects.order_by('-created')
    if not showAll:
        article_list = article_list.exclude_irrelevant()
    if news_source:
        article_list = article_list.filter(news_source__in=news_source)
    if startDate != None:
        startDate = datetime.strptime(
            "%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__gte=startDate)
    if endDate != None:
        endDate = datetime.strptime("%s 23:59:59" %
                                    endDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__lte=endDate)
    if searchTerms:
        article_list = article_list.filter(
            Q(title__icontains=searchTerms) | Q(bodytext__icontains=searchTerms))
    if categories:
        article_list = article_list.filter_categories(categories)
    if trainedRelevance:
        article_list = article_list.filter_relevant_trained(trainedRelevance)
    if categoryRelevance and categories:
        article_list = article_list.filter_trained_categories(categories, categoryRelevance)

    dateRange = Article.objects.all().aggregate(minDate=Min('created'),
                                                maxDate=Max('created'))

    data = {
        'articles': _paginate(article_list, 20, page),
        'form': form,
        'dateRange': dateRange,
    }

    return render(request, 'newsarticles/articleList.html', data)

class CrosstabSearchForm(forms.Form):
    news_source = forms.ModelMultipleChoiceField(label='News Source',
                                         required=False,
                                         widget=forms.SelectMultiple(attrs={'class':'form-control', 'size':'10'}),
                                         queryset=NewsSource.objects.all())

    startDate = forms.DateField(label='Start Date',
                                widget=forms.DateInput(format="%m/%d/%Y", attrs={'class':'form-control'}),
                                required=False)

    endDate = forms.DateField(label='End Date',
                              widget=forms.DateInput(format="%m/%d/%Y", attrs={'class':'form-control'}),
                              required=False)

    category = GroupedMultModelChoiceField(label='Categories',
                                           required=False,
                                           queryset=Category.objects.active(),
                                           group_by_field='kind',
                                           group_label=Category.KINDS.get,
                                           widget=forms.SelectMultiple(attrs={'class':'form-control', 'size':'10'}))

    categoryRelevance = forms.DecimalField(label='Category Trained Relevance (0–1)',
                                           required=False,
                                           max_value=1,
                                           min_value=0,
                                           decimal_places=2,
                                           widget=forms.NumberInput(attrs={'class':'form-control'}))

def categoryXTab(request):
    form = CrosstabSearchForm(request.POST)
    # TODO: put these into the form itself
    clearSearch = request.POST.get('clearSearch', "False") == "False"
    newSearch = request.POST.get('newSearch', "False") == "True"

    if clearSearch and newSearch and form.is_valid():
        news_source = form.cleaned_data['news_source']
        startDate = form.cleaned_data['startDate']
        endDate = form.cleaned_data['endDate']
        categories = form.cleaned_data['category']
        categoryRelevance = form.cleaned_data['categoryRelevance']

        request.session['categoryXTab_hasSearch'] = True

    elif clearSearch and request.session.get('categoryXTab_hasSearch', False):
        request.session['categoryXTab_hasSearch'] = True

        news_source = request.session['categoryXTab_news_source']
        startDate = request.session['categoryXTab_startDate']
        endDate = request.session['categoryXTab_endDate']
        categories = request.session['categoryXTab_category']
        categoryRelevance = request.session['categoryXTab_categoryRelevance']

        form = CrosstabSearchForm({
            'news_source': news_source,
            'startDate': startDate,
            'endDate': endDate,
            'categories': categories,
            'categoryRelevance': categoryRelevance
        })

    else:
        form = CrosstabSearchForm()

        news_source = []
        startDate = None
        endDate = None
        categories = []
        categoryRelevance = None

        request.session['categoryXTab_hasSearch'] = False

    request.session['categoryXTab_news_source'] = news_source
    request.session['categoryXTab_startDate'] = startDate
    request.session['categoryXTab_endDate'] = endDate
    request.session['categoryXTab_category'] = categories
    request.session['categoryXTab_categoryRelevance'] = categoryRelevance

    article_list = Article.objects.order_by()
    if news_source:
        article_list = article_list.filter(news_source__in=news_source)
    if startDate != None:
        startDate = datetime.strptime("%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__gte=startDate)
    if endDate != None:
        endDate = datetime.strptime("%s 23:59:59" % endDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__lte=endDate)
    if categories:
        article_list = article_list.filter_categories(categories)
    if categoryRelevance and categories:
        article_list = article_list.filter_trained_categories(categories, categoryRelevance)

    dateRange = Article.objects.all().aggregate(minDate=Min('created'),
                                               maxDate=Max('created'))

    category_list = {}

    for source in news_source:
        if source not in category_list:
            category_list[source] = {}
        for category in categories:
            category_query = article_list.filter(news_source=source)
            if categoryRelevance:
                category_query = category_query.filter(trainedcoding__trainedcategoryrelevance__category=category, trainedcoding__trainedcategoryrelevance__relevance__gte=categoryRelevance)
            else:
                category_query = category_query.filter(trainedcoding__trainedcategoryrelevance__category=category)
            category_list[source][category] = category_query.count()

    data = {
        'category_list': category_list,
        'categories': categories,
        'startDate': startDate,
        'endDate': endDate,
        'categoryRelevance': categoryRelevance,
        'form': form,
        'dateRange': dateRange,
    }

    return render(request, 'newsarticles/categoryXTab.html', data)

def _paginate(iter, count, pagenum):
    paginator = Paginator(iter, count)
    try:
        out = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        out = paginator.page(paginator.num_pages)

    return out


PREVIEW_LENGTH = 300


def view_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    display_text = article.bodytext

    is_preview = not request.user.is_authenticated()
    if is_preview:
        display_text = display_text[:PREVIEW_LENGTH] + '...'

    data = {'article': article,
            'is_preview': is_preview,
            'display_text': display_text}

    return render(request, 'newsarticles/article.html', data)


class UserCodingSubmitForm(forms.Form):
    relevant = forms.BooleanField(initial=True,
                                  required=False,
                                  label='Relevant')

    offend_age = forms.IntegerField(initial=None,
                                    required=False,
                                    label='Offender age (999 if undetermined)',
                                    max_value=999,
                                    min_value=0)

    offend_race = forms.ChoiceField(choices=RACE_CHOICES,
                                         required=False,
                                         label='Offender race')

    offend_ethnicity = forms.ChoiceField(choices=ETHNICITY_CHOICES,
                                         required=False,
                                         label='Offender ethnicity')

    offend_sex = forms.ChoiceField(choices=SEX_CHOICES,
                                 required=False,
                                 label='Offender sex')

    offend_name = forms.CharField(initial="",
                                  required=False,
                                  label='Offender name',
                                  max_length=128)

    offend_weap = forms.ChoiceField(choices=WEAP_CHOICES,
                                  required=False,
                                  label='Weapon')

    vict_age = forms.IntegerField(initial=None,
                                  required=False,
                                  label='Victim age (999 if undetermined)',
                                  max_value=999,
                                  min_value=0)

    vict_race = forms.ChoiceField(choices=RACE_CHOICES,
                               required=False,
                               label='Victim race')

    vict_ethnicity = forms.ChoiceField(choices=ETHNICITY_CHOICES,
                                       required=False,
                                       label='Victim ethnicity')

    vict_sex = forms.ChoiceField(choices=SEX_CHOICES,
                               required=False,
                               label='Victim sex')

    vict_name = forms.CharField(initial="",
                               required=False,
                               label='Victim name',
                               max_length=128)

    categories = GroupedMultModelChoiceField(label='Categories',
                                             required=False,
                                             queryset=Category.objects.active(),
                                             widget=forms.CheckboxSelectMultiple(),
                                             group_by_field='kind',
                                             group_label=Category.KINDS.get)

    location_data = forms.CharField(initial="[]",
                                    required=False,
                                    widget=forms.HiddenInput(attrs={'id': 'locsHiddenInput'}))

    sentiment = forms.TypedChoiceField(
        choices=SENTIMENT_CHOICES,
        required=False,
        coerce=int,
        empty_value=None,
    )

    """ Validates location_data as JSON, but doesn't check the structure at all """

    def clean_location_data(self):
        jdata = self.cleaned_data['location_data'] or '[]'
        try:
            json_data = json.loads(jdata)
        except ValueError:
            raise forms.ValidationError(
                'Invalid JSON in location_data', code='jsonerror')
        return jdata


@login_required
def code_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        form = UserCodingSubmitForm(request.POST)
        if form.is_valid():
            user_coding, created = UserCoding.objects.update_or_create(
                article=article,
                defaults={
                    'user': request.user,
                    'relevant': form.cleaned_data['relevant'],
                    'locations': form.cleaned_data['location_data'],
                    'sentiment': form.cleaned_data['sentiment'],
                    'offend_age': form.cleaned_data['offend_age'],
                    'offend_race': form.cleaned_data['offend_race'],
                    'offend_ethnicity': form.cleaned_data['offend_ethnicity'],
                    'offend_sex': form.cleaned_data['offend_sex'],
                    'offend_name': form.cleaned_data['offend_name'],
                    'offend_weap': form.cleaned_data['offend_weap'],
                    'vict_age': form.cleaned_data['vict_age'],
                    'vict_race': form.cleaned_data['vict_race'],
                    'vict_ethnicity': form.cleaned_data['vict_ethnicity'],
                    'vict_sex': form.cleaned_data['vict_sex'],
                    'vict_name': form.cleaned_data['vict_name'],
                }
            )

            # ManyToMany relationships need to be added after the record is created
            user_coding.categories.set(form.cleaned_data['categories'])

            return HttpResponseRedirect(reverse('random-article'))
    else:
        if article.is_coded():
            initial_data = {
                'categories': article.usercoding.categories.all(),
                'relevant': article.usercoding.relevant,
                'location_data': article.usercoding.locations,
                'sentiment': article.usercoding.sentiment,
                'offend_age': article.usercoding.offend_age,
                'offend_race': article.usercoding.offend_race,
                'offend_ethnicity': article.usercoding.offend_ethnicity,
                'offend_sex': article.usercoding.offend_sex,
                'offend_name': article.usercoding.offend_name,
                'offend_weap': article.usercoding.offend_weap,
                'vict_age': article.usercoding.vict_age,
                'vict_race': article.usercoding.vict_race,
                'vict_ethnicity': article.usercoding.vict_ethnicity,
                'vict_sex': article.usercoding.vict_sex,
                'vict_name': article.usercoding.vict_name,
            }
        else:
            initial_data = None

        form = UserCodingSubmitForm(initial=initial_data)

    return render(request, 'newsarticles/code_article.html',
                  {'form': form, 'article': article})


@login_required
def random_article(request):
    uncoded_relevant_article_pks = Article.objects.uncoded().values_list('pk', flat=True)
    selected_pk = random.choice(uncoded_relevant_article_pks)

    return HttpResponseRedirect(reverse('code-article', args=(selected_pk,)))


@login_required
def help(request):
    return render(request, 'newsarticles/help.html', {})
