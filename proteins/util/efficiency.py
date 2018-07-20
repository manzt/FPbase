import numpy as np
from ..models import State, Dye


def spectral_product(arrlist):
    # calculate (overlapping) product of a list of spectra.values
    # assumes monotonic increase with step = 1

    minwaves = [int(a[0][0]) for a in arrlist]
    minwave = max(minwaves)
    offsets = [minwave - i for i in minwaves]
    waverange = min([int(a[-1][0]) for a in arrlist]) - minwave
    vals = []
    for w in range(waverange + 1):
        vals.append([w + minwave, np.product([a[w + offsets[i]][1]
                     for i, a in enumerate(arrlist)])])
    return vals


def area(arr):
    area = 0
    for i in range(len(arr) - 1):
        area += (arr[i][1] + arr[i + 1][1]) / 2
    return area


def print_scope_report(report, sortby='bright', show=('bright', 'ex', 'em'), limit=10):
    form = '{:<20}' + ('{:>15}  ' * limit)
    for oc, values in report.items():
        topfluors = sorted(values.items(), key=lambda kv: kv[1][sortby])
        topfluors.reverse()
        topfluors = topfluors[:limit]
        print(form.format(oc.name, *[t[0].fluor_name for t in topfluors]))
        for item in show:
            print(form.format(item, *[t[1][item] for t in topfluors]))
        print()


def microscope_efficiency_report(scope, *args, **kwargs):
    return oclist_efficiency_report(scope.optical_configs.all(), *args, **kwargs)


def oclist_efficiency_report(oclist, fluor_collection=None, include_dyes=True):
    if fluor_collection is None:
        fluor_collection = list(State.objects.with_spectra())
        if include_dyes:
            fluor_collection += list(Dye.objects.with_spectra())
    D = {}
    for oc in oclist:
        D[oc.name] = path_efficiency_report(oc, fluor_collection)
    return D


def path_efficiency_report(oc, fluor_collection):
    # where oc is an optical config and fluor_collection is a list of a SpectrumOwner subclass
    D = {}
    oc_em = spectral_product(oc.em_spectra)
    oc_ex = spectral_product(oc.ex_spectra)
    for fluor in fluor_collection:
        D[fluor.slug] = {
            'fluor': fluor.fluor_name,
            'ex': None,
            'em': None,
            'bright': 0,
            'color': fluor.emhex,
            'ftype': 'p' if isinstance(fluor, State) else 'd',
            'url': fluor.get_absolute_url() or ''
        }
        if fluor.em_spectrum:
            combospectrum = spectral_product([oc_em, fluor.em_spectrum.data])
            D[fluor.slug]['em'] = round(area(combospectrum) / area(fluor.em_spectrum.data), 3)
        if fluor.ex_spectrum:
            combospectrum = spectral_product([oc_ex, fluor.ex_spectrum.data])
            D[fluor.slug]['ex'] = round(area(combospectrum) / area(oc_ex), 3)
        if D[fluor.slug]['em'] and D[fluor.slug]['ex'] and fluor.ext_coeff and fluor.qy:
            b = D[fluor.slug]['em'] * D[fluor.slug]['ex'] * fluor.ext_coeff * fluor.qy / 1000
            D[fluor.slug]['bright'] = round(b, 3)
    return D
