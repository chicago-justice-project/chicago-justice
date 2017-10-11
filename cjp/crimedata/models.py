from django.db import models
from django.db import connection
import datetime

class CrimeReport(models.Model):
    orig_ward = models.CharField(max_length=5, db_index=True) # character varying(5) NOT NULL,
    orig_rd   = models.CharField(max_length=20, db_index=True) #  character varying(20) NOT NULL,
    orig_beat_num = models.CharField(max_length=8, db_index=True) #  character varying(8),
    orig_location_descr = models.CharField(max_length=100, db_index=True) #  character varying(100) NOT NULL,
    orig_fbi_descr = models.CharField(max_length=100, db_index=True) #  character varying(100) NOT NULL,
    orig_domestic_i = models.CharField(max_length=4, db_index=True) #  character varying(4) NOT NULL,
    orig_status = models.CharField(max_length=50, db_index=True) #  character varying(50) NOT NULL,
    orig_street = models.CharField(max_length=100, db_index=True) #  character varying(100) NOT NULL,
    orig_fbi_cd = models.CharField(max_length=10, db_index=True) #  character varying(10) NOT NULL,
    orig_dateocc = models.CharField(max_length=50, db_index=True) #  character varying(50) NOT NULL,
    orig_stnum = models.CharField(max_length=20, db_index=True) #  character varying(20) NOT NULL,
    orig_description = models.CharField(max_length=150, db_index=True) #  character varying(150) NOT NULL,
    orig_stdir = models.CharField(max_length=10, db_index=True) #  character varying(10) NOT NULL,
    orig_curr_iucr = models.CharField(max_length=20, db_index=True) #  character varying(20) NOT NULL,

    web_case_num = models.CharField(max_length=20, db_index=True) #   character varying(20) NOT NULL,
    web_date = models.DateTimeField(db_index=True)                # timestamp without time zone NOT NULL,
    web_block = models.CharField(max_length=200, db_index=True) #   character varying(200) NOT NULL,
    web_code = models.CharField(max_length=20, db_index=True) #   character varying(20) NOT NULL,
    web_crime_type = models.CharField(max_length=100, db_index=True) #   character varying(100) NOT NULL,
    web_secondary = models.CharField(max_length=150, db_index=True) #   character varying(150) NOT NULL,
    web_arrest = models.CharField(max_length=1, db_index=True) #   character(1) NOT NULL,
    web_location = models.CharField(max_length=100, db_index=True) #   character varying(100) NOT NULL,
    web_domestic = models.CharField(max_length=4, db_index=True) #   character varying(4) NOT NULL,
    web_beat = models.CharField(max_length=8, db_index=True) #   character varying(8) NOT NULL,
    web_ward = models.CharField(max_length=5, db_index=True) #   character varying(5) NOT NULL,
    web_nibrs = models.CharField(max_length=11, db_index=True) #   character varying(11) NOT NULL,

    crime_date = models.DateField(db_index=True) # date NOT NULL,
    crime_time = models.TimeField(db_index=True)

    geocode_latitude = models.FloatField(db_index=True) #  double precision NOT NULL,
    geocode_longitude = models.FloatField(db_index=True) #  double precision NOT NULL


class LookupCRCrimeDateMonth(models.Model):
    year = models.SmallIntegerField(db_index=True)
    month = models.SmallIntegerField(db_index=True)
    the_date = models.DateField()

    @staticmethod
    def createLookup():
        LookupCRCrimeDateMonth.objects.all().delete()
        months = CrimeReport.objects.extra(select={
                                            'month_date': "to_char(crime_date, 'YYYY-MM')",
                                            'the_month' : 'extract(month from crime_date)',
                                            'the_year'  : 'extract(year from crime_date)'})
        months = months.values('month_date', 'the_month', 'the_year').order_by('month_date').distinct()
        for m in months:
            lcrm  = LookupCRCrimeDateMonth(year=int(m['the_year']),
                                           month=int(m['the_month']),
                                           the_date=datetime.date(int(m['the_year']), int(m['the_month']), 1))
            lcrm.save()

    def __str__(self):
        return "{}-{:02d}".format(self.year, self.month)


class LookupCRCode(models.Model):
    web_code = models.CharField(max_length=20, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRCode.objects.all().delete()
        codes = CrimeReport.objects.all().values('web_code').order_by('web_code').distinct()

        for code in codes:
            lcr = LookupCRCode(web_code=code['web_code'])
            lcr.save()

    def __str__(self):
        return self.web_code


class LookupCRCrimeType(models.Model):
    web_crime_type = models.CharField(max_length=100, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRCrimeType.objects.all().delete()
        crimeTypes = CrimeReport.objects.all().values('web_crime_type').order_by('web_crime_type').distinct()

        for crimeType in crimeTypes:
            if len(crimeType['web_crime_type']) > 0:
                lcrt = LookupCRCrimeType(web_crime_type=crimeType['web_crime_type'])
                lcrt.save()

    def __str__(self):
        return self.web_crime_type

class LookupCRSecondary(models.Model):
    web_secondary = models.CharField(max_length=150, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRSecondary.objects.all().delete()
        secondaries = CrimeReport.objects.all().values('web_secondary').order_by('web_secondary').distinct()

        for secondary in secondaries:
            if len(secondary['web_secondary']) > 0:
                lcrs = LookupCRSecondary(web_secondary=secondary['web_secondary'])
                lcrs.save()

    def __str__(self):
        return self.web_secondary

class LookupCRBeat(models.Model):
    web_beat = models.CharField(max_length=8, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRBeat.objects.all().delete()
        beats = CrimeReport.objects.all().values('web_beat').order_by('web_beat').distinct()

        for beat in beats:
            if len(beat['web_beat']) > 0:
                lcrb = LookupCRBeat(web_beat=beat['web_beat'])
                lcrb.save()

    def __str__(self):
        return self.web_beat

class LookupCRWard(models.Model):
    web_ward = models.CharField(max_length=5, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRWard.objects.all().delete()
        wards = CrimeReport.objects.all().values('web_ward').order_by('web_ward').distinct()

        for ward in wards:
            if len(ward['web_ward']) > 0:
                lcrw = LookupCRWard(web_ward=ward['web_ward'])
                lcrw.save()

    def __str__(self):
        return self.web_ward

class LookupCRNibrs(models.Model):
    web_nibrs = models.CharField(max_length=11, db_index=True)

    @staticmethod
    def createLookup():
        LookupCRNibrs.objects.all().delete()
        nibrss = CrimeReport.objects.all().values('web_nibrs').order_by('web_nibrs').distinct()

        for nibrs in nibrss:
            if len(nibrs['web_nibrs']) > 0:
                lcrn = LookupCRNibrs(web_nibrs=nibrs['web_nibrs'])
                lcrn.save()

    def __str__(self):
        return self.web_nibrs
