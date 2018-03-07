"""
Helper functions for migrations. Try to treat this file as append-only, as
changes to functions could break past migrations.
"""

import gc

def queryset_iterator(queryset, chunksize=1000):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    """
    queryset = queryset.order_by('pk')
    last_item = queryset.last()

    if not last_item:
        return

    pk = 0
    while pk < last_item.pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()