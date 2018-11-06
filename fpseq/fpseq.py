import json
from .skbio_protein import SkbSequence
from .util import protein_weight, slugify
from .align import nw_align, align_seqs, parental_numbering
from .mutations import find_mutations, mutate_sequence
try:
    import requests
except ImportError:
    print('Could not import requests. Cannot pull sequences from fpbase')


def generate_labels(seq, mods=None, zeroindex=1):
    """generate a list of len(seq), with position labels, possibly modified"""
    i = zeroindex
    if not mods:
        return [str(x) for x in range(i, len(seq) + i)]
    else:
        if isinstance(mods, list):
            mods = dict(mods)
        pos_labels = []
        for n in range(i, len(seq) + i):
            if n in mods:
                pos_labels.append(str(mods[n]))
            else:
                pos_labels.append(str(i))
                i += 1
        return pos_labels


def from_fpbase(slug):
    url = 'https://www.fpbase.org/api/{}/?format=json'.format(slugify(slug))
    response = requests.get(url)
    return FPSeq(json.loads(response.content).get('seq'))


class FPSeq(SkbSequence):

    def __init__(self, sequence, position_lables=None, **kwargs):
        super().__init__(sequence, **kwargs)
        self._poslabels = generate_labels(str(self), position_lables)

    @property
    def weight(self):
        try:
            return protein_weight(str(self)) / 1000
        except ValueError:
            pass

    def align_to(self, other, **kwargs):
        return nw_align(str(self), str(other), **kwargs)

    def mutations_to(self, other, reference=None, **kwargs):
        return find_mutations(str(self), other, reference)

    def positions_relative_to(self, reference):
        return parental_numbering(*align_seqs(self, reference))

    def mutate(self, mutations, **kwargs):
        result = mutate_sequence(str(self), mutations, **kwargs)
        if 'correct_offset' in kwargs:
            return FPSeq(result[0]), result[1]
        return FPSeq(result)

    @classmethod
    def from_fpbase(cls, slug):
        return from_fpbase(slug)