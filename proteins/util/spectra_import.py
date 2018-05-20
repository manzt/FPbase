import numpy as np
from ..forms import SpectrumForm


def zip_wave_data(waves, data, minmax=None):
    minmax = minmax or (300, 1600)
    return [list(i) for i in zip(waves, data) if (i[1] > 0 and minmax[0] <= i[0] <= minmax[1])]


def get_stype(header):
    if '(2p)' in header.lower():
        return '2p'
    if any(x in header.lower() for x in ('(ab', 'absorption')):
        return 'ab'
    if any(x in header.lower() for x in ('(em', 'emission')):
        return 'em'
    if any(x in header.lower() for x in ('(ex', 'excitation')):
        return 'ex'


# FIXME: I kind of hate this function...
def import_spectral_data(waves, data, headers=None, categories=[],
                         stypes=[], owner=None, minmax=None):
    '''
    Take a vector of waves and a matrix of data, and import into database

    if cat or stype are strings, they will be assigned to all spectra
    they can also be a list of strings with the same length as the number of
    data columns (not including waves) in the file
    '''
    if isinstance(categories, (list, tuple)) and len(categories):
        assert len(categories) == len(data), 'provided category list not the same length as data'
    elif isinstance(categories, str):
        categories = [categories] * len(data)
    else:
        raise ValueError('Must provide category, or list of categories with same length as data')

    if isinstance(stypes, (list, tuple)) and len(stypes):
        assert len(stypes) == len(data), 'provided subtypes list not the same length as data'
    elif isinstance(stypes, str):
        stypes = [stypes] * len(data)
    else:
        stypes = [None] * len(data)

    if not headers:
        headers = [None] * len(data)

    newObjects = []
    errors = []
    for datum, header, cat, stype in zip(data, headers, categories, stypes):
        if not(any(datum)) or all(np.isnan(datum)):
            print("skipping col {} ... no data".format(header))
            continue

        if not stype:
            stype = get_stype(header)

        iowner = owner
        if not iowner:
            iowner = header.split(' (')[0]

        D = zip_wave_data(waves, datum, minmax)
        sf = SpectrumForm({'data': D, 'category': cat, 'subtype': stype, 'owner': iowner})
        if sf.is_valid():
            newob = sf.save()
            newObjects.append(newob)
            print('Successfully imported {}, {}, {}'.format(iowner, cat, stype))
        else:
            errors.append((iowner, sf.errors))

    return newObjects, errors
