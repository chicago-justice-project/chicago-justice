FROM python:2
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV DJANGO_SETTINGS_MODULE="cjp.settings.local"
ENV SECRET_KEY='#&ubnzmo6$-0nk7i&hmii=e$7y-)nv+bm#&ps)6eq@!k+n-nq5'
ADD . .
EXPOSE 8000
CMD [ "./setup_db.sh" ]
