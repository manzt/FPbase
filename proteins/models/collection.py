from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from model_utils.models import TimeStampedModel


User = get_user_model()


class OwnedCollection(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=512, blank=True)
    owner = models.ForeignKey(User, blank=True, null=True,
                              related_name='%(class)s' + 's',
                              on_delete=models.SET_NULL,)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class ProteinCollection(OwnedCollection):
    proteins = models.ManyToManyField('Protein', related_name='collection_memberships')
    private = models.BooleanField(default=False, verbose_name="Private Collection",
                                  help_text="Private collections can not be seen "
                                            "by or shared with other users")

    def get_absolute_url(self):
        return reverse("proteins:collection-detail", args=[self.id])

    class Meta:
        unique_together = (('owner', 'name'),)
