import logging
from django.core.management.base import BaseCommand

from newsarticles.backfills import outdated

LOG = logging.getLogger(__name__)

BACKFILL_TYPE_OUTDATED = 'outdated'

class Command(BaseCommand):
    help = "Re-run tagging on articles"

    def add_arguments(self, parser):
        parser.add_argument('backfill_type', nargs='?')

    def handle(self, *args, **options):
        backfill = options.get('backfill_type', BACKFILL_TYPE_OUTDATED)

        if backfill == BACKFILL_TYPE_OUTDATED:
            LOG.info('Running backfill on outdated articles')
            outdated.run()
