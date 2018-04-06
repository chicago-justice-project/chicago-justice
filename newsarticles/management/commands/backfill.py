import logging
from django.core.management.base import BaseCommand

from newsarticles.backfills import outdated

LOG = logging.getLogger(__name__)

BACKFILL_TYPE_OUTDATED = 'outdated'

class Command(BaseCommand):
    help = "Re-run tagging on articles"

    def add_arguments(self, parser):
        parser.add_argument('backfill_type', nargs='?', default=BACKFILL_TYPE_OUTDATED)

    def handle(self, *args, **options):
        if options['backfill_type'] == BACKFILL_TYPE_OUTDATED:
            LOG.info('Running backfill on outdated articles')
            outdated.run()
