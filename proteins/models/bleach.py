# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from model_utils.models import TimeStampedModel
from references.models import Reference
from .mixins import Authorable


class BleachMeasurement(Authorable, TimeStampedModel):
    POINTSCANNER = 'ps'
    SPINNINGDISC = 'sd'
    WIDEFIELD = 'wf'
    TIRF = 't'
    SPECTROPHOTOMETER = 's'
    OTHER = 'o'
    MODALITY_CHOICES = (
        (WIDEFIELD, 'Widefield'),
        (POINTSCANNER, 'Point Scanning Confocal'),
        (SPINNINGDISC, 'Spinning Disc Confocal'),
        (SPECTROPHOTOMETER, 'Spectrophotometer'),
        (TIRF, 'TIRF'),
        (OTHER, 'Other'),
    )

    ARCLAMP = 'a'
    LASER = 'la'
    LED = 'le'
    OTHER = 'o'
    LIGHT_CHOICES = (
        (ARCLAMP, 'Arc-lamp'),
        (LASER, 'Laser'),
        (LED, 'LED'),
        (OTHER, 'Other'),
    )

    UNKNOWN = -1
    NO = 0
    YES = 1
    INCELL_CHOICES = (
        (UNKNOWN, 'Unkown'),
        (NO, 'No'),
        (YES, 'Yes'),
    )

    rate      = models.FloatField(verbose_name='Bleach Rate', help_text="Photobleaching half-life (s)",
                validators=[MinValueValidator(0), MaxValueValidator(3000)])  # bleaching half-life
    power     = models.FloatField(null=True, blank=True, verbose_name='Illumination Power',
                validators=[MinValueValidator(-1)], help_text="If not reported, use '-1'",)
    units     = models.CharField(max_length=100, blank=True, verbose_name='Power Unit', help_text="e.g. W/cm2",)
    light     = models.CharField(max_length=2, choices=LIGHT_CHOICES, blank=True, verbose_name='Light Source')
    modality  = models.CharField(max_length=2, choices=MODALITY_CHOICES, blank=True, verbose_name='Imaging Modality')
    temp      = models.FloatField(null=True, blank=True, verbose_name='Temperature',)
    fusion    = models.CharField(max_length=60, blank=True, verbose_name='Fusion Protein', help_text="(if applicable)",)
    in_cell   = models.IntegerField(default=-1, choices=INCELL_CHOICES, blank=True, verbose_name='In cells?', help_text="protein expressed in living cells",)

    reference = models.ForeignKey(Reference, related_name='bleach_measurements', verbose_name="Measurement Reference", blank=True, null=True, on_delete=models.SET_NULL, help_text="Reference where the measurement was made",)  # usually, the original paper that published the protein
    state     = models.ForeignKey('State', related_name='bleach_measurements', verbose_name="Protein (state)", help_text="The state on which this measurement was made", on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}{}".format(
            self.state,
            '{} s'.format(self.rate) if self.rate else '',
            'with'.format(self.modality) if self.modality else '')
