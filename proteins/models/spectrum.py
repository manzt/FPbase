import numpy as np
import ast
import json
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.forms import Textarea, CharField
from model_utils.models import TimeStampedModel
from model_utils.managers import QueryManager
from .mixins import Authorable, Product
from ..util.helpers import wave_to_hex
from scipy import interpolate
from scipy.signal import argrelextrema, savgol_filter


def is_monotonic(array):
    array = np.array(array)
    return np.all(array[1:] > array[:-1])


def make_monotonic(x, y):
    X, Y = list(zip(*sorted(zip(x, y))))
    X, xind = np.unique(X, return_index=True)
    Y = np.array(Y)[xind]
    return X, Y


def interp_linear(x, y, s=1):
    '''Interpolate pair of vectors at integer increments between min(x) and max(x)'''
    if not is_monotonic(x):
        x, y = make_monotonic(x, y)
    xnew = range(int(np.ceil(min(x))), int(np.floor(max(x))))
    F = interpolate.interp1d(x, y)
    ynew = F(xnew)
    ynew = savgol_filter(ynew, 9, 2)
    return xnew, ynew


def interp_univar(x, y, s=1):
    if not is_monotonic(x):
        x, y = make_monotonic(x, y)
    '''Interpolate pair of vectors at integer increments between min(x) and max(x)'''
    xnew = range(int(np.ceil(min(x))), int(np.floor(max(x))))
    F = interpolate.InterpolatedUnivariateSpline(x, y)
    ynew = F(xnew)
    # ynew = savgol_filter(ynew, 15, 2)
    return xnew, ynew


def norm2one(y):
    return [round(max(yy / max(y), 0), 4) for yy in y]


def norm2P(y):
    '''Normalize peak value of vector to one'''
    y = np.array(y)
    localmax = argrelextrema(y, np.greater, order=100)
    # can't be within first 10 points
    localmax = [i for i in localmax[0] if i > 10]
    maxind = localmax[np.argmax(y[localmax])]
    maxy = y[maxind]
    return [round(max(yy / maxy, 0), 4) for yy in y], maxy, maxind


class SpectrumData(ArrayField):

    def __init__(self, base_field=None, size=None, **kwargs):
        if not base_field:
            base_field = ArrayField(models.FloatField(max_length=10), size=2)
        super().__init__(base_field, size, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'max_length': self.size,
            'widget': Textarea(attrs={'cols': '102', 'rows': '15'}),
            'form_class': CharField,
        }
        defaults.update(kwargs)
        return models.Field().formfield(**defaults)

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, str):
            try:
                return ast.literal_eval(value)
            except Exception:
                raise ValidationError('Invalid input for spectrum data')

    def value_to_string(self, obj):
        return json.dumps(self.value_from_object(obj))

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        for elem in value:
            if not len(elem) == 2:
                raise ValidationError("All elements in Spectrum list must have two items")
            if not all(isinstance(n, (int, float)) for n in elem):
                raise ValidationError("All items in Septrum list elements must be numbers")


class SpectrumOwner(Authorable):
    name        = models.CharField(max_length=100)  # required
    slug        = models.SlugField(max_length=128, unique=True, help_text="Unique slug for the %(class)")  # calculated at save

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.slug)

    def save(self, *args, **kwargs):
        self.slug = self.makeslug()
        super().save(*args, **kwargs)

    def makeslug(self):
        return slugify(self.name)

    def d3_dicts(self):
        return [spect.d3dict() for spect in self.spectra.all()]


class Filter(SpectrumOwner, Product):
    bandcenter = models.PositiveSmallIntegerField(blank=True, null=True,
                    validators=[MinValueValidator(200), MaxValueValidator(1600)])
    bandwidth  = models.PositiveSmallIntegerField(blank=True, null=True,
                    validators=[MinValueValidator(300), MaxValueValidator(900)])
    edge       = models.FloatField(null=True, blank=True,
                    validators=[MinValueValidator(0), MaxValueValidator(200)])
    tavg       = models.FloatField(blank=True, null=True,
                    validators=[MinValueValidator(0), MaxValueValidator(1)])
    aoi        = models.PositiveSmallIntegerField(blank=True, null=True,
                    validators=[MinValueValidator(0), MaxValueValidator(90)])

    def save(self, *args, **kwargs):
        if '/' in self.name:
            try:
                w = self.name.split('/')[0].split(' ')[-1]
                self.bandcenter = int("".join([i for i in w[:4] if i.isdigit()]))
                w = self.name.split('/')[1].split(' ')[0]
                self.bandwidth = int("".join([i for i in w[:4] if i.isdigit()]))
            except Exception:
                pass

        if self.bandcenter and self.bandwidth:
            try:
                if self.spectra.count() == 1:
                    wrange = ((self.bandcenter - self.bandwidth / 2) + 2,
                              (self.bandcenter + self.bandwidth / 2) - 2)
                    self.tavg = self.spectra.first().avg(wrange)
            except Exception:
                pass
        super().save(*args, **kwargs)


class Camera(SpectrumOwner, Product):
    manufacturer = models.CharField(max_length=128, blank=True)


class Light(SpectrumOwner, Product):
    manufacturer = models.CharField(max_length=128, blank=True)


class SpectrumManager(models.Manager):
    def state_slugs(self):
        L = self.get_queryset().exclude(owner_state=None).values_list(
            'owner_state__slug', 'owner_state__protein__name', 'owner_state__name').distinct()
        return [(slug, prot if state == 'default' else '{} ({})'.format(prot, state)) for slug, prot, state in L]

    def dye_slugs(self):
        return self.get_queryset().filter(category=self.DYE).values_list(
            'owner_dye__slug', 'owner_dye__name').distinct()

    def sluglist(self):
        ''' probably using this one going forward for spectra page'''
        Q = self.get_queryset().values(
            'category', 'subtype', 'owner_state__protein__name',
            'owner_state__slug', 'owner_dye__slug', 'owner_filter__slug',
            'owner_light__slug', 'owner_camera__slug', 'owner_state__name',
            'owner_dye__name', 'owner_filter__name', 'owner_light__name',
            'owner_camera__name')

        out = []
        for v in Q:
            slug = (v['owner_state__slug'] or v['owner_dye__slug'] or
                    v['owner_filter__slug'] or v['owner_light__slug'] or
                    v['owner_camera__slug'])
            name = (v['owner_dye__name'] or v['owner_filter__name'] or
                    v['owner_light__name'] or v['owner_camera__name'] or None)
            if not name:
                prot = v['owner_state__protein__name']
                state = v['owner_state__name']
                name = prot if state == 'default' else '{} ({})'.format(prot, state)
            out.append({
                'category': v['category'],
                'subtype': v['subtype'],
                'slug': slug,
                'name': name,
            })
        return sorted(out, key=lambda k: k['name'])

    def owner_slugs(self):
        ''' unused? '''
        L = self.get_queryset().exclude(owner_state=None).values_sluglist(
            'owner_state__slug', 'owner_state__protein__name',
            'owner_state__name', 'category', 'subtype').distinct()
        out = [(slug, prot, cat if state == 'default' else '{} ({})'.format(prot, state))
               for slug, prot, state, cat in L]

        for n in ('dye', 'light', 'filter', 'camera'):
            out += self.get_queryset().exclude(**{'owner_' + n: None}).values_list(
                *['owner_' + n + '__slug', 'owner_' + n + '__name', 'category', 'subtype']).distinct()

        out.sort(key=lambda x: x[1], reverse=False)

        return out

    def filter_owner(self, slug):
        qs = self.none()
        A = ('owner_state', 'owner_dye', 'owner_filter', 'owner_light', 'owner_camera')
        for ownerclass in A:
            qs = qs | self.get_queryset().filter(**{ownerclass + '__slug': slug})
        return qs


class Spectrum(Authorable, TimeStampedModel):

    DYE = 'd'
    PROTEIN = 'p'
    LIGHT = 'l'
    FILTER = 'f'
    CAMERA = 'c'
    CATEGORIES = (
        (DYE, 'Dye'),
        (PROTEIN, 'Protein'),
        (LIGHT, 'Light Source'),
        (FILTER, 'Filter'),
        (CAMERA, 'Camera'),
    )

    EX = 'ex'
    ABS = 'ab'
    EM = 'em'
    TWOP = '2p'
    BP = 'bp'
    BPX = 'bx'  # bandpass excitation filter
    BPM = 'bm'
    SP = 'sp'
    LP = 'lp'
    BS = 'bs'  # dichroic
    QE = 'qe'
    PD = 'pd'
    SUBTYPE_CHOICES = (
        (EX, 'Excitation'),                 # for fluorophores
        (ABS, 'Absorption'),                # for fluorophores
        (EM, 'Emission'),                   # for fluorophores
        (TWOP, 'Two Photon Absorption'),    # for fluorophores
        (BP,  'Bandpass'),                  # only for filters
        (BPX, 'Bandpass (Excitation)'),     # only for filters
        (BPM, 'Bandpass (Emission)'),       # only for filters
        (SP, 'Shortpass'),                  # only for filters
        (LP, 'Longpass'),                   # only for filters
        (BS, 'Beamsplitter'),               # only for filters
        (QE, 'Quantum Efficiency'),         # only for cameras
        (PD, 'Power Distribution'),         # only for light sources
    )

    # not all subtypes are valid for all categories
    category_subtypes = {
        DYE: [EX, ABS, EM, TWOP],
        PROTEIN: [EX, ABS, EM, TWOP],
        FILTER: [BP, BPX, BPM, SP, LP, BS],
        CAMERA: [QE],
        LIGHT: [PD],
    }

    data     = SpectrumData()
    category = models.CharField(max_length=1, choices=CATEGORIES, verbose_name='Item Type', db_index=True)
    subtype  = models.CharField(max_length=2, choices=SUBTYPE_CHOICES, blank=True, verbose_name='Spectra Subtype', db_index=True)
    ph       = models.FloatField(null=True, blank=True, verbose_name='pH')  # pH of measurement
    solvent  = models.CharField(max_length=128, blank=True)

    owner_state = models.ForeignKey('State', null=True, blank=True, on_delete=models.CASCADE, related_name='spectra')
    owner_dye = models.ForeignKey('Dye', null=True, blank=True, on_delete=models.CASCADE, related_name='spectra')
    owner_filter = models.ForeignKey('Filter', null=True, blank=True, on_delete=models.CASCADE, related_name='spectra')
    owner_light = models.ForeignKey('Light', null=True, blank=True, on_delete=models.CASCADE, related_name='spectra')
    owner_camera = models.ForeignKey('Camera', null=True, blank=True, on_delete=models.CASCADE, related_name='spectra')

    objects  = SpectrumManager()
    proteins = QueryManager(category=PROTEIN)
    dyes     = QueryManager(category=DYE)
    lights   = QueryManager(category=LIGHT)
    filters  = QueryManager(category=FILTER)
    cameras  = QueryManager(category=CAMERA)

    class Meta:
        verbose_name_plural = "spectra"

    def __str__(self):
        if self.owner_state:
            return "{} {}".format(self.owner_state if self.owner_state else 'unowned', self.subtype)
        else:
            return self.name

    def save(self, *args, **kwargs):
        # FIXME: figure out why self.full_clean() throws validation error with
        # 'data cannot be null' ... even if data is provided...
        # self.full_clean()
        if not any(self.owner_set):
            raise ValidationError("Spectrum must have an owner!")
        if sum(bool(x) for x in self.owner_set) > 1:
            raise ValidationError("Spectrum must have only one owner!")
        #self.category = self.owner.__class__.__name__.lower()[0]
        super().save(*args, **kwargs)

    def clean(self):
        # model-wide validation after individual fields have been cleaned
        errors = {}
        if self.category == self.CAMERA:
            self.subtype = self.QE
        if self.category == self.LIGHT:
            self.subtype = self.PD
        if self.category in self.category_subtypes:
            if self.subtype not in self.category_subtypes[self.category]:
                errors.update({
                    'subtype': '{} spectrum subtype must be{} {}'.format(
                        self.get_category_display(),
                        '' if len(self.category_subtypes[self.category]) > 1 else '  one of:',
                        ' '.join(self.category_subtypes[self.category])
                    )
                })

        if errors:
            raise ValidationError(errors)

        if self.data:
            if self.step > 10 and len(self.data) < 10:
                errors.update({'data': 'insufficient data'})
            else:
                if self.step != 1:
                    try:
                        # TODO:  better choice of interpolation
                        if self.subtype == self.TWOP:
                            self.data = [list(i) for i in zip(*interp_linear(self.x, self.y))]
                        else:
                            self.data = [list(i) for i in zip(*interp_univar(self.x, self.y))]
                    except ValueError as e:
                        errors.update({'data': 'could not properly interpolate data: {}'.format(e)})
                        raise ValidationError(errors)
                # attempt at data normalization
                if (max(self.y) > 1.5) or (max(self.y) < 0.1):
                    if self.category == self.FILTER and (60 < max(self.y) < 101):
                        # assume 100% scale
                        self.change_y([round(yy/100, 4) for yy in self.y])
                    elif (self.category == self.PROTEIN and self.subtype == self.TWOP):
                        y, self._peakval2p, maxi = norm2P(self.y)
                        self._peakwave2p = self.x[maxi]
                        self.change_y(y)
                    else:
                        self.change_y(norm2one(self.y))

        if errors:
            raise ValidationError(errors)

    @property
    def owner_set(self):
        return [self.owner_state, self.owner_dye, self.owner_filter,
                self.owner_light, self.owner_camera]

    @property
    def owner(self):
        return next((x for x in self.owner_set if x), None)
        #  raise AssertionError("No owner is set")

    @property
    def name(self):
        # this method allows the protein name to have changed in the meantime
        if self.owner_state:
            if self.owner_state.name == 'default':
                return "{} {}".format(self.owner_state.protein, self.subtype)
            else:
                return "{} {}".format(self.owner_state, self.subtype)
        else:
            return "{} {}".format(self.owner, self.subtype)

    @property
    def peak_wave(self):
        try:
            if self.min_wave < 300:
                return self.x[self.y.index(max([i for n, i in enumerate(self.y) if self.x[n] > 300]))]
            else:
                try:
                    # first look for the value 1
                    # this is to avoid false 2P peaks
                    return self.x[self.y.index(1)]
                except ValueError:
                    return self.x[self.y.index(max(self.y))]
        except ValueError:
            return False

    @property
    def min_wave(self):
        return self.data[0][0]

    @property
    def max_wave(self):
        return self.data[-1][0]

    @property
    def step(self):
        s = set()
        for i in range(len(self.x)-1):
            s.add(self.x[i+1] - self.x[i])
        if len(s) > 1:  # multiple step sizes
            return False
        return list(s)[0]

    def scaled_data(self, scale):
        return [[n[0], n[1] * scale] for n in self.data]

    def color(self):
        return wave_to_hex(self.peak_wave)

    def waverange(self, waverange):
        assert len(waverange) == 2, 'waverange argument must be an iterable of len 2'
        return [d for d in self.data if waverange[0] <= d[0] <= waverange[1]]

    def avg(self, waverange):
        d = self.waverange(waverange)
        return np.mean([i[1] for i in d])

    def width(self, height=0.5):
        try:
            upindex = next(x[0] for x in enumerate(self.y) if x[1] > height)
            downindex = len(self.y) - next(x[0] for x in enumerate(reversed(self.y)) if x[1] > height)
            return (self.x[upindex], self.x[downindex])
        except Exception:
            return False

    def d3dict(self, area=True):
        D = {
            "slug": self.owner.slug,
            "key": self.name,
            "values": self.d3data(),
            "peak": self.peak_wave,
            "minwave": self.min_wave,
            "maxwave": self.max_wave,
            "category": self.category,
            "type": self.subtype,
            "color": self.color(),
            "area": area,
            "url": self.owner.get_absolute_url(),
        }

        if self.category == self.CAMERA:
            D["color"] = 'url(#crosshatch)'
        elif self.category == self.LIGHT:
            D["color"] = 'url(#wavecolor_gradient)'

        if self.category in (self.PROTEIN, self.DYE):
            if self.subtype == self.EX:
                D.update({
                    'scalar': self.owner.ext_coeff,
                    'ex_max': self.owner.ex_max,
                })
            elif self.subtype == self.EM:
                D.update({
                    'scalar': self.owner.qy,
                    'em_max': self.owner.em_max,
                })
            elif self.subtype == self.TWOP:
                D.update({
                    'scalar': self.owner.twop_peakGM,
                    'twop_qy': self.owner.twop_qy
                })
        return D

    def d3data(self):
        return [{'x': elem[0], 'y': elem[1]} for elem in self.data]

    def wave_value_pairs(self):
        output = {}
        # arrayLength = len(self.data)
        for elem in self.data:
            output[elem[0]] = elem[1]
        return output

    @property
    def x(self):
        self._x = []
        for i in self.data:
            self._x.append(i[0])
        return self._x

    @property
    def y(self):
        self._y = []
        for i in self.data:
            self._y.append(i[1])
        return self._y

    # def change_x(self, value):
    #     if not isinstance(value, list):
    #         raise TypeError("X values must be a python list")
    #     if len(value) != len(self.data):
    #         raise ValueError("Error: array length must match existing data")
    #     for i in range(len(value)):
    #         self.data[i][0] = value[i]

    def change_y(self, value):
        if not isinstance(value, list):
            raise TypeError("Y values must be a python list")
        if len(value) != len(self.data):
            raise ValueError("Error: array length must match existing data")
        for i in range(len(value)):
            self.data[i][1] = value[i]
