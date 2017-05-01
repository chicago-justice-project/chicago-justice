from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q, Max, Min
from django.shortcuts import render, get_object_or_404
from django import forms
from newsarticles.models import Article, Category, NewsSource, UserCoding


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

    category = forms.ModelMultipleChoiceField(label='Category',
                                              required=False,
                                              queryset=Category.objects.all())

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

    categories = forms.ModelMultipleChoiceField(label='Categories',
                                                required=False,
                                                widget=forms.CheckboxSelectMultiple(),
                                                queryset=Category.objects.all())

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
                    'relevant': form.cleaned_data['relevant']})

            # ManyToMany relationships need to be added after the record is created
            user_coding.categories = form.cleaned_data['categories']

            return HttpResponseRedirect(reverse('mainArticleView'))
    else:
        if article.is_coded():
            initial_data = {'categories': article.usercoding.categories.all(),
                            'relevant': article.usercoding.relevant}
        else:
            initial_data = None

        form = UserCodingSubmitForm(initial=initial_data)

    return render(request, 'newsarticles/code_article.html',
                  {'form': form, 'article': article})
