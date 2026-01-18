# Chicago Justice Project - Backend Application

## Project Overview

The Chicago Justice Project (CJP) backend is a Django-based data journalism platform that scrapes, categorizes, and analyzes crime and justice-related news articles from Chicago media sources. The platform enables researchers and journalists to track how crime is reported in local news.

### Key Capabilities
- **News scraping** from multiple Chicago media outlets
- **Article coding** - Manual categorization by users
- **ML-powered classification** - Automated category prediction using the `tagnews` library
- **Sentiment analysis** - Analyze tone of articles toward police entities
- **Geolocation extraction** - Identify locations mentioned in articles
- **Crime data integration** - Chicago Police Department crime report data

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Framework | Django 4.2 |
| Database | PostgreSQL |
| API | Django REST Framework |
| ML/NLP | TensorFlow, Keras, scikit-learn, NLTK, tagnews |
| Scraping | feedparser, BeautifulSoup4 |
| Deployment | AWS Elastic Beanstalk |
| Server | Gunicorn |

## Project Structure

```
chicago-justice/
├── cjp/                    # Django project settings
│   └── settings/           # Environment-specific settings (base, local, production)
├── newsarticles/           # Core app: articles, scraping, coding, tagging
│   ├── scrapers/           # News source scrapers
│   └── management/commands/# Django management commands
├── crimedata/              # Crime report data from CPD
│   └── scrapers/           # CPD data scraper
├── cjpusers/               # User authentication
├── stats/                  # Analytics views
├── templates/              # HTML templates
├── staticfiles/            # CSS, JS, fonts
├── scripts/                # Utility scripts
├── .ebextensions/          # AWS EB configuration
└── requirements.txt        # Python dependencies
```

## Core Django Apps

### newsarticles
The primary app containing:
- **Models**: Article, NewsSource, Category, ScraperResult, UserCoding, TrainedCoding
- **Scrapers**: Multiple news source scrapers in `newsarticles/scrapers/`
- **Tagging**: ML-based article classification using `tagnews` library (`tagging.py`)
- **API**: REST endpoints for articles, categories, and trained codings

### crimedata
Chicago crime report data:
- **Models**: CrimeReport with geographic data (ward, beat, coordinates)
- **Scraper**: CPD data scraper (`cpdScraper.py`)

### cjpusers
User authentication and management

### stats
Analytics and statistics views

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL

### Quick Start

1. **Create PostgreSQL database**:
   ```shell
   createdb cjpdb
   createuser --interactive --pwprompt
   psql -d postgres -c "GRANT ALL ON DATABASE cjpdb TO cjpuser;"
   ```

2. **Set up environment**:
   ```shell
   cp .env-example .env
   # Edit .env with your database credentials
   ```

3. **Install dependencies**:
   ```shell
   pip install -r requirements.txt
   ```

4. **Initialize database**:
   ```shell
   ./manage.py migrate
   ./manage.py loaddata category news_source
   ```

5. **Run development server**:
   ```shell
   ./manage.py runserver
   ```

### Environment Variables

Required variables (see `.env-example`):
- `DJANGO_SETTINGS_MODULE` - Settings module (e.g., `cjp.settings.local`)
- `SECRET_KEY` - Django secret key
- `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`
- `KERAS_BACKEND` - Set to `tensorflow`
- `GOOGLE_ANALYTICS_KEY` - For analytics tracking
- `EXPORT_TOKEN` - For S3 database exports

## Common Commands

### Running Scrapers
```shell
# Run all scrapers
./manage.py runscrapers

# Run specific scraper
./manage.py runscrapers crains
```

Scrapers are scheduled via cron jobs in production.

### Other Management Commands
- `./manage.py runsentiment` - Run sentiment analysis
- `./manage.py downloadcorpus` - Download NLTK corpus
- `./manage.py backfill` - Backfill article data
- `./manage.py import` - Import data

## API Endpoints

Key REST API routes:
- `GET /api/articles/` - List articles
- `GET /api/categories/` - List categories
- `GET /api/trained-codings/` - ML-generated classifications
- `POST /api/articles/{id}/trained-coding/` - Get/create trained coding

Authentication: Token-based + Session-based

## ML/NLP Pipeline

The project uses the `tagnews` library (developed for CJP) for:
- **Crime category prediction** - Classifies articles into crime/policing categories
- **Location extraction** - Identifies Chicago locations in article text
- **Sentiment analysis** - Uses Google Cloud NLP API for sentiment scoring

Models are loaded lazily and cached via `@lru_cache` in `newsarticles/tagging.py`.

For local `tagnews` development:
```shell
pip install -e PATH_TO_ARTICLE_TAGGING_REPO
```

## Deployment

### AWS Elastic Beanstalk

1. **Install EB CLI**:
   ```shell
   pip install awsebcli
   ```

2. **Configure credentials**:
   ```shell
   export AWS_ACCESS_KEY_ID=XXXXXX
   export AWS_SECRET_ACCESS_KEY=XXXXXX
   ```

3. **Deploy**:
   ```shell
   eb deploy
   ```

Deployment automatically runs:
- Database migrations
- NLTK corpus download
- Static file collection

## Code Style

- **Linting**: pylint (see `.pylintrc`)
- Follow existing code patterns and Django conventions

## Testing

Testing infrastructure is not yet implemented.

## Related Repositories

- [article-tagging](https://github.com/chicago-justice-project/article-tagging) - The `tagnews` ML library
