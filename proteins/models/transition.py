# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from model_utils.models import TimeStampedModel


class StateTransition(TimeStampedModel):
    trans_wave = models.PositiveSmallIntegerField(
            blank=True,
            null=True,
            verbose_name='Transition Wavelength',
            help_text="Wavelength required",
            validators=[MinValueValidator(300), MaxValueValidator(1000)]
            )
    protein = models.ForeignKey('Protein',
        related_name='transitions',
        verbose_name="Protein Transitioning",
        help_text="The protein that demonstrates this transition",
        on_delete=models.CASCADE)
    from_state = models.ForeignKey('State',
            related_name='transitions_from',
            verbose_name="From state",
            help_text="The initial state ",
            on_delete=models.CASCADE)
    to_state = models.ForeignKey('State',
            related_name='transitions_to',
            verbose_name="To state",
            help_text="The state after transition",
            on_delete=models.CASCADE)

    def clean(self):
        errors = {}
        if self.from_state.protein != self.protein:
            errors.update({'from_state': '"From" state must belong to protein {}'.format(self.protein.name)})
        if self.to_state.protein != self.protein:
            errors.update({'to_state': '"To" state must belong to protein {}'.format(self.protein.name)})
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return "Transition: {} {} -> {}".format(self.protein.name,
            self.from_state.name, self.to_state.name)