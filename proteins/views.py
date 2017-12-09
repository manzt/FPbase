from django.views.generic import DetailView, ListView
from django.http import Http404
from django.shortcuts import render, redirect
from .models import Protein
from .forms import ProteinSearchForm, ProteinSubmitForm
from django.core import serializers


class ProteinChartList(ListView):
    ''' renders html for single protein page  '''
    template_name = 'ichart.html'
    model = Protein
    queryset = Protein.objects.filter(switch_type=Protein.BASIC).select_related('default_state')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        filtered_data = []
        filtered_data = serializers.serialize('json', self.get_queryset,
            fields=('name', 'default_state__em_max')
        )
        print(filtered_data)
        context['data'] = filtered_data
        return context


class ProteinDetailView(DetailView):
    ''' renders html for single protein page  '''
    model = Protein


def protein_table(request):
    ''' renders html for single protein page  '''
    return render(request, 'table.html', {"proteins": Protein.objects.select_related('default_state')})


def submit(request):
    form = ProteinSubmitForm()
    return render(request, 'submit.html', {'form': form})


def search(request):
    # this is the logic for when the user goes straight to the search page
    # or when they come in from the home page with a GET search
    if request.method == 'GET':
        #client = swiftype.Client(api_key=settings.SWIFTYPE_API_KEY)
        try:
            q = request.GET['q']
        except:
            return render(request, 'search.html', {'form': ProteinSearchForm(initial={'ex_range': '10', 'em_range': '10'})})

        # this was from (can't remember name) search engine
        #response = client.search_document_type('engine', 'proteins', q)
        #if response['status'] == 200:
        #    query = response['body']
            # proteins = [Protein.objects.get(id=record['external_id']) for record in query['records']['proteins']]
        #    id_list = [record['external_id'] for record in query['records']['proteins']]

        proteins = Protein.objects.filter(name__icontains=request.GET['q'])
        # if there's only a single result, just go to that page
        if proteins.count() == 1:
            return redirect(proteins.first())
        form = ProteinSearchForm(
            initial={'name': q, 'ex_range': '10', 'em_range': '10'}
        )
        return render(request, 'search.html', {'proteins': proteins, 'form': form})
    # this is the logic for when the user hits the submit button
    elif request.method == 'POST':
        form = ProteinSearchForm(request.POST, initial={'ex_range': '10'})
        if form.is_valid():
            q = form.data
            proteins = Protein.objects.filter(
                name__icontains=q['name'],
            )
            if q['switch_type']:
                proteins = proteins.filter(switch_type=q['switch_type'])
            if q['agg']:
                proteins = proteins.filter(agg=q['agg'])
            if q['parent_organism']:
                proteins = proteins.filter(parent_organism=q['parent_organism'])

            if q['ex_max']:
                m = float(q['ex_max'])
                if q['ex_range']:
                    r = float(q['ex_range'])/2.
                else:
                    r = 5
                proteins = proteins.filter(states__ex_max__lte=(m+r), states__ex_max__gte=(m-r))
            if q['em_max']:
                m = float(q['em_max'])
                if q['em_range']:
                    r = float(q['em_range'])/2.
                else:
                    r = 5
                proteins = proteins.filter(states__em_max__lte=(m+r), states__em_max__gte=(m-r))
            # if there's only a single result, just go to that page
            if proteins.count() == 1:
                return redirect(proteins.first())
            return render(request, 'search.html', {'proteins': proteins.order_by('default_state__em_max'), 'form': form})
        else:
            return render(request, 'search.html', {'form': form})
    else:
        assert False
        form = ProteinSearchForm(
            initial={'name': 'I love your site!'}
        )
