# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

from .mixins import Product
from .spectrum import SpectrumOwner
from ..util.helpers import wave_to_hex


class Fluorophore(SpectrumOwner):
    ex_max      = models.PositiveSmallIntegerField(blank=True, null=True,
                    validators=[MinValueValidator(300), MaxValueValidator(900)], db_index=True)
    em_max      = models.PositiveSmallIntegerField(blank=True, null=True,
                    validators=[MinValueValidator(300), MaxValueValidator(1000)], db_index=True)
    twop_ex_max = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Peak 2P excitation',
                    validators=[MinValueValidator(700), MaxValueValidator(1600)], db_index=True)
    ext_coeff   = models.IntegerField(blank=True, null=True,
                    validators=[MinValueValidator(0), MaxValueValidator(300000)],
                    verbose_name="Extinction Coefficient")  # extinction coefficient
    twop_peakGM = models.FloatField(null=True, blank=True, verbose_name='Peak 2P cross-section of S0->S1 (GM)',
                    validators=[MinValueValidator(0), MaxValueValidator(200)])
    qy          = models.FloatField(null=True, blank=True, verbose_name="Quantum Yield",
                    validators=[MinValueValidator(0), MaxValueValidator(1)])  # quantum yield
    twop_qy     = models.FloatField(null=True, blank=True, verbose_name="2P Quantum Yield",
                    validators=[MinValueValidator(0), MaxValueValidator(1)])  # quantum yield
    brightness  = models.FloatField(null=True, blank=True, editable=False)
    pka         = models.FloatField(null=True, blank=True, verbose_name='pKa',
                    validators=[MinValueValidator(2), MaxValueValidator(12)])  # pKa acid dissociation constant
    lifetime    = models.FloatField(null=True, blank=True, help_text="Lifetime (ns)",
                    validators=[MinValueValidator(0), MaxValueValidator(20)])  # fluorescence lifetime in nanoseconds

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.qy and self.ext_coeff:
            self.brightness = float(round(self.ext_coeff * self.qy / 1000, 2))
        super().save(*args, **kwargs)

    @property
    def abs_spectra(self):
        spect = self.spectra.filter(subtype='ab')
        if spect.count() > 1:
            raise AssertionError('multiple abs spectra found')
        return spect.first() or None

    @property
    def ex_spectra(self):
        spect = self.spectra.filter(subtype='ex')
        if spect.count() > 1:
            raise AssertionError('multiple ex spectra found')
        return spect.first() or None

    @property
    def em_spectra(self):
        spect = self.spectra.filter(subtype='em')
        if spect.count() > 1:
            raise AssertionError('multiple em spectra found')
        return spect.first() or None

    @property
    def twop_spectra(self):
        spect = self.spectra.filter(subtype='2p')
        if spect.count() > 1:
            raise AssertionError('multiple 2p spectra found')
        return spect.first() or None

    @property
    def bright_rel_egfp(self):
        if self.brightness:
            return self.brightness / .336
        return None

    @property
    def stokes(self):
        try:
            return self.em_max - self.ex_max
        except TypeError:
            return None

    @property
    def emhex(self):
        return wave_to_hex(self.em_max)

    @property
    def exhex(self):
        return wave_to_hex(self.ex_max)

    def has_spectra(self):
        if any([self.ex_spectra, self.em_spectra, self.twop_spectra]):
            return True
        return False

    def ex_band(self, height=0.7):
        return self.ex_spectra.width(height)

    def em_band(self, height=0.7):
        return self.em_spectra.width(height)

    def within_ex_band(self, value, height=0.7):
        if self.has_spectra():
            minRange, maxRange = self.ex_band(height)
            if minRange < value < maxRange:
                return True
        return False

    def within_em_band(self, value, height=0.7):
        if self.has_spectra():
            minRange, maxRange = self.em_band(height)
            if minRange < value < maxRange:
                return True
        return False

    def d3_dicts(self):
        return [spect.d3dict() for spect in self.spectra.all()]


class Dye(Fluorophore, Product):
    pass


class StatesManager(models.Manager):
    def notdark(self):
        return self.filter(is_dark=False)


class State(Fluorophore):
    DEFAULT_NAME = 'default'

    """ A class for the states that a given protein can be in (including spectra and other state-dependent properties)  """
    name        = models.CharField(max_length=64, default=DEFAULT_NAME)  # required
    is_dark     = models.BooleanField(default=False, verbose_name="Dark State", help_text="This state does not fluorescence",)
    maturation  = models.FloatField(null=True, blank=True, help_text="Maturation time (min)",  # maturation half-life in min
                                    validators=[MinValueValidator(0), MaxValueValidator(1600)])
    # Relations
    transitions = models.ManyToManyField('State', related_name='transition_state', verbose_name="State Transitions", blank=True, through='StateTransition')  # any additional papers that reference the protein
    protein     = models.ForeignKey('Protein', related_name="states", help_text="The protein to which this state belongs", on_delete=models.CASCADE)

    # Managers
    objects = StatesManager()

    class Meta:
        verbose_name = u'State'
        unique_together = (("protein", "ex_max", "em_max", "ext_coeff", "qy"),)

    def __str__(self):
        if self.name in (self.DEFAULT_NAME, 'default'):
            return str(self.protein.name)
        return "{} ({})".format(self.protein.name, self.name)

    def get_absolute_url(self):
        return self.protein.get_absolute_url()

    def makeslug(self):
        return self.protein.slug + '_' + slugify(self.name)

    @property
    def local_brightness(self):
        """ brightness relative to spectral neighbors.  1 = average """
        if not (self.em_max and self.brightness):
            return 1
        B = State.objects.exclude(id=self.id).filter(
                em_max__around=self.em_max).aggregate(Avg('brightness'))
        try:
            v = round(self.brightness / B['brightness__avg'], 4)
        except TypeError:
            v = 1
        return v
