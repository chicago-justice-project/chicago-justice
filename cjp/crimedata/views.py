from crimedata.models import CrimeReport, LookupCRCrimeDateMonth, LookupCRCode, LookupCRCrimeType, LookupCRSecondary, LookupCRBeat, LookupCRWard, LookupCRNibrs
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import forms
from django.http import HttpResponse
from django.db.models import Q, Max, Min
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.db import connection
import csv
import datetime
import time

class CrimeReportForm(forms.Form):

    caseNum = forms.CharField(label='case num', required=False, max_length=20)

    codes = LookupCRCode.objects.all()
    codeList = tuple((c.web_code, c.web_code) for c in codes)
    code = forms.ChoiceField(label='code',
                             choices=(('', ''), ) + codeList,
                             required=False)

    crimeTypes = LookupCRCrimeType.objects.all()
    crimeTypeList = tuple((c.web_crime_type, c.web_crime_type) for c in crimeTypes)
    crimeType = forms.ChoiceField(label='crime type',
                                    choices=(('', ''), ) + crimeTypeList,
                                    required=False)

    secondaries = LookupCRSecondary.objects.all()
    secondaryList = tuple((c.web_secondary, c.web_secondary) for c in secondaries)
    secondary = forms.ChoiceField(label='secondary',
                                    choices=(('', ''), ) + secondaryList,
                                    required=False)

    location = forms.CharField(label='location', required=False, max_length=100)
    block = forms.CharField(label='block', required=False, max_length=200)
    startDate = forms.DateField(label='start date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)
    endDate = forms.DateField(label='end date',
                                widget=forms.DateInput(format="%m/%d/%Y"),
                                required=False)
    arrest = forms.ChoiceField(label='arrest',
                                 choices=(('', ''), ('Y', 'Yes'), ('N', 'No')),
                                 required=False)
    domestic = forms.ChoiceField(label='domestic',
                                 choices=(('', ''), ('Y', 'Yes'), ('N', 'No')),
                                 required=False)

    beats = LookupCRBeat.objects.all()
    beatList = tuple((c.web_beat, c.web_beat) for c in beats)
    beat = forms.ChoiceField(label='beat',
                             choices=(('', ''), ) + beatList,
                             required=False)

    wards = LookupCRWard.objects.all()
    wardList = tuple((c.web_ward, c.web_ward) for c in wards)
    ward = forms.ChoiceField(label='ward',
                             choices=(('', ''), ) + wardList,
                             required=False)

    nibrss = LookupCRNibrs.objects.all()
    nibrsList = tuple((c.web_nibrs, c.web_nibrs) for c in nibrss)
    nibrs = forms.ChoiceField(label='nibrs',
                             choices=(('', ''), ) + nibrsList,
                             required=False)

class CrimeReportExportForm(forms.Form):
    months = ["%d-%02d" % (m.year, m.month) for m in LookupCRCrimeDateMonth.objects.all()]
    months = tuple((m, m) for m in months)

    dateGroup = forms.ChoiceField(label='Month',
                                 choices=((('', ''), ) + months),
                                 required=False)

def crimeReportList(request):
    form = CrimeReportForm(request.POST)
    clearSearch = request.POST.get('clearSearch', "False") == "False"
    newSearch = request.POST.get('newSearch', "False") == "True"

    if clearSearch and newSearch and form.is_valid():
        caseNum = form.cleaned_data['caseNum'].strip()
        block = form.cleaned_data['block'].strip().upper()
        location = form.cleaned_data['location'].strip().upper()
        arrest = form.cleaned_data['arrest'].strip().upper()
        if arrest not in ('Y', 'N'):
            arrest = None
        code = form.cleaned_data['code']
        crimeType = form.cleaned_data['crimeType']
        secondary = form.cleaned_data['secondary']
        domestic = form.cleaned_data['domestic']
        if domestic not in ('Y', 'N'):
            domestic = None
        beat = form.cleaned_data['beat']
        ward = form.cleaned_data['ward']
        nibrs = form.cleaned_data['nibrs']
        startDate = form.cleaned_data['startDate']
        endDate = form.cleaned_data['endDate']

        page = 1

        request.session['crimeData_hasSearch'] = True

    elif clearSearch and request.session.get('crimeData_hasSearch', False):
        request.session['crimeData_hasSearch'] = True

        caseNum = request.session['crimeData_caseNum']
        block = request.session['crimeData_block']
        location = request.session['crimeData_location']
        arrest = request.session['crimeData_arrest']
        code = request.session['crimeData_code']
        crimeType = request.session['crimeData_crimeType']
        secondary = request.session['crimeData_secondary']
        domestic = request.session['crimeData_domestic']
        beat = request.session['crimeData_beat']
        ward = request.session['crimeData_ward']
        nibrs = request.session['crimeData_nibrs']
        startDate = request.session['crimeData_startDate']
        endDate = request.session['crimeData_endDate']

        form = CrimeReportForm({
            'caseNum' : caseNum,
            'block' : block,
            'location' : location,
            'arrest' : arrest,
            'code' : code,
            'crimeType' : crimeType,
            'secondary' : secondary,
            'domestic' : domestic,
            'beat' : beat,
            'ward' : ward,
            'nibrs' : nibrs,
            'startDate' : startDate,
            'endDate' : endDate,
        })

        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('crimeData_page', 1)
    else:
        form = CrimeReportForm()

        caseNum = None
        block = None
        location = None
        arrest = None
        code = None
        crimeType = None
        secondary = None
        domestic = None
        beat = None
        ward = None
        nibrs = None
        startDate = None
        endDate = None

        # 3/2/2012 John Nicholson
        # added so paging works even when there is no search
        try:
            page = int(request.POST.get('page', 'invalid'))
        except ValueError:
            page = request.session.get('crimeData_page', 1)

        request.session['crimeData_hasSearch'] = False

    request.session['crimeData_caseNum'] = caseNum
    request.session['crimeData_block'] = block
    request.session['crimeData_location'] = location
    request.session['crimeData_arrest'] = arrest
    request.session['crimeData_code'] = code
    request.session['crimeData_crimeType'] = crimeType
    request.session['crimeData_secondary'] = secondary
    request.session['crimeData_domestic'] = domestic
    request.session['crimeData_beat'] = beat
    request.session['crimeData_ward'] = ward
    request.session['crimeData_nibrs'] = nibrs
    request.session['crimeData_startDate'] = startDate
    request.session['crimeData_endDate'] = endDate
    request.session['crimeData_page'] = page

    crimeReport_list = CrimeReport.objects.all().order_by('-web_date')
    if caseNum:
        crimeReport_list = crimeReport_list.filter(web_case_num__contains=caseNum)
    if block:
        crimeReport_list = crimeReport_list.filter(web_block__contains=block)
    if location:
        crimeReport_list = crimeReport_list.filter(web_location__contains=location)
    if arrest:
        crimeReport_list = crimeReport_list.filter(web_arrest=arrest)
    if code:
        crimeReport_list = crimeReport_list.filter(web_code=code)
    if crimeType:
        crimeReport_list = crimeReport_list.filter(web_crime_type=crimeType)
    if secondary:
        crimeReport_list = crimeReport_list.filter(web_secondary=secondary)
    if domestic:
        crimeReport_list = crimeReport_list.filter(web_domestic=domestic)
    if beat:
        crimeReport_list = crimeReport_list.filter(web_beat=beat)
    if ward:
        crimeReport_list = crimeReport_list.filter(web_ward=ward)
    if nibrs:
        crimeReport_list = crimeReport_list.filter(web_nibrs=nibrs)
    if startDate:
        startDate = datetime.datetime.strptime("%s 00:00:00" % startDate, "%Y-%m-%d %H:%M:%S")
        crimeReport_list = crimeReport_list.filter(web_date__gte=startDate)
    if endDate:
        endDate = datetime.datetime.strptime("%s 23:59:59" % endDate, "%Y-%m-%d %H:%M:%S")
        crimeReport_list = crimeReport_list.filter(web_date__lte=endDate)

    paginator = Paginator(crimeReport_list, 20) # Show 2 articles per page

    try:
        crimeReports = paginator.page(page)
    except (EmptyPage, InvalidPage):
        crimeReports = paginator.page(paginator.num_pages)

    dateRange = CrimeReport.objects.all().aggregate(minDate = Min('web_date'),
                                                    maxDate = Max('web_date'))

    data = {'crimeReports' : crimeReports,
            'form' : form,
            'exportForm' : CrimeReportExportForm(),
            'dateRange' : dateRange,
           }
    return render(request, 'crimedata/crimeReportList.html', data)


def crimeReportView(request, crimeReportId):
    try:
        crimeReport = CrimeReport.objects.get(id = crimeReportId)
    except:
        crimeReport = None

    template = 'crimedata/crimeReport.html'

    data = {'crimeReport' : crimeReport}
    return render(request, template, data)


def crimeReportExport(request):
    '''
    export a month of data
    '''

    dateGroup = request.GET.get('dateGroup', '').strip()
    if not dateGroup:
        return HttpResponse()

    crimeReport_list = CrimeReport.objects.all()

    try:
        result = time.strptime(dateGroup, '%Y-%m')
        startDay = datetime.date(*result[:3])

        if startDay.month != 12:
            endDay = datetime.date(startDay.year, startDay.month + 1, 1)
        else:
            endDay = datetime.date(startDay.year + 1, 1, 1)

        crimeReport_list = crimeReport_list.filter(crime_date__gte = startDay).filter(crime_date__lt = endDay)
    except Exception, e:
        # not a valid month
        return HttpResponse()

    crimeReport_list = crimeReport_list.order_by('web_date')

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=crimeReport.csv'

    fields = [
        'web_case_num',
        'web_date',
        'web_block',
        'web_code',
        'web_crime_type',
        'web_secondary',
        'web_arrest',
        'web_location',
        'web_domestic',
        'web_beat',
        'web_ward',
        'web_nibrs',
    ]

    if request.user.is_authenticated():
        fields += [
            'orig_rd',
            'orig_dateocc',
            'orig_stnum',
            'orig_stdir',
            'orig_street',
            'orig_curr_iucr',
            'orig_fbi_descr',
            'orig_fbi_cd',
            'orig_description',
            'orig_status',
            'orig_location_descr',
            'orig_domestic_i',
            'orig_ward',
            'orig_beat_num',

            'crime_date',
            'crime_time',

            'geocode_longitude',
            'geocode_latitude',
        ]

    writer = csv.writer(response,quoting=csv.QUOTE_ALL )
    writer.writerow(fields)
    cnt = 0
    for cr in crimeReport_list.iterator():
        data = [str(getattr(cr, fname)) for fname in fields]
        writer.writerow(data)

    return response
