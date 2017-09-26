import json
import random
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q, Max, Min
from django.shortcuts import render, get_object_or_404
from django import forms
from newsarticles.models import Article, Category, NewsSource, UserCoding
from newsarticles.forms import GroupedMultModelChoiceField


class ArticleSearchForm(forms.Form):
    showAll = forms.BooleanField(label='Show Non-Crime',
                                 initial=False, required=False)

    news_source = forms.ModelChoiceField(label='Source',
                                         required=False,
                                         empty_label='All Sources',
                                         queryset=NewsSource.objects.all())

    startDate = forms.DateField(label='Start Date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)

    endDate = forms.DateField(label='End Date',
                              widget=forms.DateInput(format="%m/%d/%Y"),
                              required=False)

    searchTerms = forms.CharField(label='Search Terms', required=False,
                                  max_length=1024)

    category = GroupedMultModelChoiceField(label='Categories',
                                           required=False,
                                           queryset=Category.objects.active(),
                                           group_by_field='kind',
                                           group_label=Category.KINDS.get)

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

        form = ArticleSearchForm({
            'showAll': showAll,
            'news_source': news_source,
            'startDate': startDate,
            'endDate': endDate,
            'searchTerms': searchTerms,
            'categories': categories
        })

        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('article_page', 1)

    else:
        form = ArticleSearchForm()

        showAll = False
        news_source = None
        startDate = None
        endDate = None
        searchTerms = ''
        categories = []

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

    article_list = Article.objects.order_by('-created')
    if not showAll:
        article_list = article_list.exclude_irrelevant()
    if news_source:
        article_list = article_list.filter(news_source=news_source)
    if startDate != None:
        startDate = datetime.strptime("%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__gte=startDate)
    if endDate != None:
        endDate = datetime.strptime("%s 23:59:59" % endDate, "%Y-%m-%d %H:%M:%S")
        article_list = article_list.filter(created__lte=endDate)
    if searchTerms:
        article_list = article_list.filter(Q(title__icontains=searchTerms) | Q(bodytext__icontains=searchTerms))
    if categories:
        article_list = article_list.filter_categories(categories)

    dateRange = Article.objects.all().aggregate(minDate = Min('created'),
                                                maxDate = Max('created'))

    data = {
        'articles': _paginate(article_list, 20, page),
        'form': form,
        'dateRange': dateRange,
    }

    return render(request, 'newsarticles/articleList.html', data)

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

    categories = GroupedMultModelChoiceField(label='Categories',
                                             required=False,
                                             queryset=Category.objects.active(),
                                             widget=forms.CheckboxSelectMultiple(),
                                             group_by_field='kind',
                                             group_label=Category.KINDS.get)

    location_data = forms.CharField(initial="[]",
                                    required=False,
                                    widget=forms.HiddenInput(attrs={'id': 'locsHiddenInput'}))

    """ Validates location_data as JSON, but doesn't check the structure at all """
    def clean_location_data(self):
        jdata = self.cleaned_data['location_data'] or '[]'
        try:
            json_data = json.loads(jdata)
        except ValueError:
            raise forms.ValidationError('Invalid JSON in location_data', code='jsonerror')
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
                    'locations': form.cleaned_data['location_data']})

            # ManyToMany relationships need to be added after the record is created
            user_coding.categories = form.cleaned_data['categories']

            return HttpResponseRedirect(reverse('random-article'))
    else:
        if article.is_coded():
            initial_data = {'categories': article.usercoding.categories.all(),
                            'relevant': article.usercoding.relevant,
                            'location_data': article.usercoding.locations}
        else:
            initial_data = None

        form = UserCodingSubmitForm(initial=initial_data)

    return render(request, 'newsarticles/code_article.html',
                  {'form': form, 'article': article})

@login_required
def random_article(request):
    uncoded_article_pks = Article.objects.uncoded().values_list('pk', flat=True)
    selected_pk = random.choice(uncoded_article_pks)
    
    return HttpResponseRedirect(reverse('code-article', args=(selected_pk,)))
