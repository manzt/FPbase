import os
import tablib
import re
import numpy as np
import requests
from django.core.validators import URLValidator
from django.template.defaultfilters import slugify
from ..forms import SpectrumForm


############################################
#       Importing Tools
############################################


BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_stype(header):
    if '(2p)' in header.lower():
        return '2p'
    if any(x in header.lower() for x in ('(ab', 'absorption')):
        return 'ab'
    if any(x in header.lower() for x in ('(em', 'emission')):
        return 'em'
    if any(x in header.lower() for x in ('(ex', 'excitation')):
        return 'ex'


def zip_wave_data(waves, data, minmax=None):
    minmax = minmax or (300, 1600)
    return [list(i) for i in zip(waves, data) if (i[1] > 0 and minmax[0] <= i[0] <= minmax[1])]


def fetch_chroma_url(url):
    '''
    url is either a Chroma ASCII text url:
    https://www.chroma.com/file/69074/download?token=nMjkwb45
    or a chroma token:
    'nMjkwb45'
    '''

    urlv = URLValidator()

    try:
        urlv(url)
    except Exception:
        raise ValueError('invalid url for Chroma download')

    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise ValueError('ASCII download failed')


def fetch_chroma_part(part):
    ''' Retrieve ASCII spectra for a chroma part number

    part is a string:
    'ET525/50m' or 'et525-50m'
    must resolve to a url such as:
    https://www.chroma.com/products/parts/et525-50m
    '''
    from html.parser import HTMLParser

    class ChromaParser(HTMLParser):
        ready = 0
        url = False

        def handle_starttag(self, tag, attrs):
            if self.ready == 0:
                if tag == 'span' and len(attrs):
                    for k, v in attrs:
                        if k == 'class' and v == 'file':
                            self.ready = 1
            elif self.ready == 1:
                if tag == 'a' and len(attrs):
                    for k, v in attrs:
                        if k == 'href' and 'download?token' in v:
                            self.url = v
                            self.ready = 2

    part = part.replace('/', '-')
    chromaURL = 'https://www.chroma.com/products/parts/'
    response = requests.get(chromaURL + slugify(part))
    if response.status_code == 200:
        parser = ChromaParser()
        parser.feed(response.text)
        if parser.url:
            return fetch_chroma_url(parser.url)
        else:
            raise ValueError('Found Chroma part {}, but could not find file to download'.format(slugify(part)))
    else:
        raise ValueError('Could not retrieve Chroma part: {}'.format(slugify(part)))


def normalize_semrock_part(part):
    return re.sub('-(25|35)$', '', part)

def fetch_semrock_part(part):
    ''' Retrieve ASCII spectra for a semrock part number

    part is a string:
   'FF01-571/72' or  'FF01-571/72-25' (-25) will be clipped
    must resolve to a url such as:
    https://www.semrock.com/_ProductData/Spectra/FF01-571_72_Spectrum.txt
    '''

    part = normalize_semrock_part(part)
    part = part.replace('/', '_').upper()
    semrockURL = 'https://www.semrock.com/_ProductData/Spectra/'
    url = semrockURL + slugify(part) + '_Spectrum.txt'
    try:
        urlv = URLValidator()
        urlv(url)
    except Exception:
        raise ValueError('invalid url for Semrock download: {}'.format(url))

    response = requests.get(url)
    if response.status_code == 200:
        T = response.text
        if T.startswith('Typical') and 'Data format' in T:
            T = T.split('Data format')[1]
            T = "".join(T.split('\n')[1:])
            T = T.split('---')[0]
            T = T.strip('\r').replace('\r', '\n')
        return T
    else:
        raise ValueError('Could not retrieve Semrock part: {}'.format(part))


def text_to_spectra(text, wavecol=0):
    try:
        # find the first string, split on multiple tokens
        float(re.split(';|,|\n|\t', text)[0])
        data = tablib.Dataset().load(text, headers=[])
    except ValueError:
        # first number is not a float... probably a header
        data = tablib.Dataset().load(text)
    waves = np.array([x if x else 0 for x in data.get_col(wavecol)], dtype='f')
    headers = data.headers
    if headers:
        headers.pop(wavecol)

    outdata = np.zeros((data.width - 1, data.height), dtype='f')
    if data.height:
        s = 0
        for column in range(data.width):
            if column == wavecol:
                s = 1
                continue
            outdata[column - s] = np.array([x if x else np.nan for x in data.get_col(column)], dtype='f')

    return waves, outdata, headers


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


def import_chroma_spectra(part=None, url=None, **kwargs):
    if isinstance(part, str):
        text = fetch_chroma_part(part)
        kwargs['owner'] = 'Chroma ' + part
        if part.lower().endswith(('m', 'em')):
            kwargs['stypes'] = 'bm'
        elif part.lower().endswith(('ex', 'x', 'bp')):
            kwargs['stypes'] = 'bx'
        elif ('rpc' in part) or ('bs' in part):
            kwargs['stypes'] = 'bs'
        elif 'lp' in part:
            kwargs['stypes'] = 'lp'
        elif 'sp' in part:
            kwargs['stypes'] = 'sp'
        if 'stypes' not in kwargs:
            raise ValueError('Could not guess filter type for part {}'.format(part))
    elif url:
        if 'owner' not in kwargs:
            raise ValueError('must provide argument "owner" when importing from url')
        if 'stypes' not in kwargs:
            raise ValueError('must provide argument "stypes" when importing from url')
        text = fetch_chroma_url(url)
    else:
        ValueError('did not receive appropriate input to import_chroma_spectra')
    waves, data, headers = text_to_spectra(text)

    kwargs['categories'] = 'f'
    newObjects, errors = import_spectral_data(waves, data, headers, **kwargs)
    for obj in newObjects:
        obj.owner.manufacturer = 'Chroma'
        obj.owner.part = part
        obj.owner.save()
    return newObjects, errors


def import_semrock_spectra(part=None, **kwargs):
    if isinstance(part, str):
        part = normalize_semrock_part(part)
        text = fetch_semrock_part(part)
        kwargs['owner'] = 'Semrock ' + part

        kwargs['stypes'] = 'bp'  # default to bandpass
        if 'sp' in part.lower():
            kwargs['stypes'] = 'sp'
        if 'lp' in part.lower():
            kwargs['stypes'] = 'lp'
        if ('di' in part.lower()) or len([i for i in part if i == '/']) > 1:
            kwargs['stypes'] = 'bs'
        if re.search(r'(\d+)/(\d+)', part):
            w1, w2 = re.search(r'(\d+)/(\d+)', part).groups()
            if w2 > w1:  # likely a dichroic
                kwargs['stypes'] = 'bs'
        if 'stypes' not in kwargs:
            raise ValueError('Could not guess filter type for part {}'.format(part))
    else:
        ValueError('did not receive appropriate input to import_semrock_spectra')
    waves, data, headers = text_to_spectra(text)

    kwargs['categories'] = 'f'

    newObjects, errors = import_spectral_data(waves, data, headers, **kwargs)
    for obj in newObjects:
        obj.owner.manufacturer = 'Semrock'
        obj.owner.part = part
        obj.owner.save()

    return newObjects, errors


#########################
#  Conversion
#########################
