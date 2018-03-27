from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django import forms
from django.urls import resolve, reverse_lazy
from django.core.mail import mail_admins

import json
from ..models import ProteinCollection
from ..forms import CollectionForm


def serialized_proteins_response(queryset, format='json', filename='FPbase_proteins'):
    from proteins.api.serializers import ProteinSerializer as PS
    PS.Meta.on_demand_fields = ()
    serializer = PS(queryset, many=True)
    if format == 'json':
        from rest_framework.renderers import JSONRenderer as rend
        response = JsonResponse(serializer.data, safe=False)
    elif format == 'csv':
        from rest_framework_csv.renderers import CSVStreamingRenderer as rend
        from django.http import StreamingHttpResponse
        response = StreamingHttpResponse(rend().render(serializer.data), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    return response


class CollectionList(ListView):
    def get_queryset(self):
        # get all collections for current user and all other non-private collections
        qs = ProteinCollection.objects.exclude(private=True)
        if self.request.user.is_authenticated:
            qs = qs | ProteinCollection.objects.filter(owner=self.request.user)
        if 'owner' in self.kwargs:
            qs = qs.filter(owner__username=self.kwargs['owner'])
        return qs.order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'owner' in self.kwargs:
            context['owner'] = self.kwargs['owner']
        return context

class CollectionDetail(DetailView):
    queryset = ProteinCollection.objects.all().prefetch_related('proteins', 'proteins__states', 'proteins__default_state')

    def get(self, request, *args, **kwargs):
        format = request.GET.get('format', '').lower()
        if format in ('json', 'csv'):
            col = self.get_object()
            return serialized_proteins_response(col.proteins.all(), format,
                    filename=slugify(col.name))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['isowner'] = self.request.user == self.object.owner
        return context

    def render_to_response(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            if self.object.private and (self.object.owner != self.request.user):
                return render(self.request, 'proteins/private_collection.html', {'foo': 'bar'})
        return super().render_to_response(*args, **kwargs)


@login_required
def collection_remove(request):
    if not request.is_ajax():
        return HttpResponseNotAllowed([])
    try:
        protein = int(request.POST["target_protein"])
        collection = int(request.POST["target_collection"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    col = get_object_or_404(ProteinCollection, id=collection)

    if not col.owner == request.user:
        return HttpResponseNotAllowed([])
    col.proteins.remove(protein)
    response = {
        'status': 'deleted',
    }
    return JsonResponse(response)


@login_required
def add_to_collection(request):
    if not request.is_ajax():
        return HttpResponseNotAllowed([])

    if request.method == 'GET':
        qs = ProteinCollection.objects.filter(owner=request.user)
        widget = forms.Select(attrs={'class': 'form-control custom-select', 'id': 'collectionSelect'})
        choicefield = forms.ChoiceField(choices=qs.values_list('id', 'name'), widget=widget)

        members = []
        if request.GET.get('id'):
            try:
                qs = qs.filter(proteins=int(request.GET.get('id')))
                members = [(item.name, item.get_absolute_url()) for item in qs]
            except Exception as e:
                print(e)
                pass

        response = {
            'widget': choicefield.widget.render('collectionChoice', ''),
            'members': json.dumps(members),
        }
        return JsonResponse(response)

    elif request.method == 'POST':
        try:
            collection = ProteinCollection.objects.get(id=request.POST.get('collectionChoice'))
            collection.proteins.add(int(request.POST.get('protein')))
            status = 'success'
        except Exception as e:
            status = 'error'
            print(e)
        return JsonResponse({'status': status})

    return HttpResponseNotAllowed([])


class CollectionCreateView(CreateView):
    model = ProteinCollection
    form_class = CollectionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        if len(self.request.POST.getlist('protein')):
            kwargs['proteins'] = self.request.POST.getlist('protein')
        elif self.request.POST.get('dupcollection', False):
            id = self.request.POST.get('dupcollection')
            kwargs['proteins'] = [p.id for p in ProteinCollection.objects.get(id=id).proteins.all()]
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        if getattr(form, 'proteins', None):
            self.object.proteins.add(*form.proteins)
        if not self.request.user.is_staff:
            mail_admins('Collection Created',
                "User: {}\nCollection: {}\n{}".format(
                    self.request.user.username,
                    self.object,
                    self.request.build_absolute_uri(self.object.get_absolute_url())),
                fail_silently=True)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        redirect_url = self.request.POST.get('next') or self.request.GET.get('next', None)
        try:
            # check that this is an internal redirection
            resolve(redirect_url)
        except Exception:
            redirect_url = None
        return redirect_url or super().get_success_url()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST.get('colname', False):
            data['colname'] = self.request.POST.get('colname')
        return data


class CollectionUpdateView(UpdateView):
    model = ProteinCollection
    form_class = CollectionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class CollectionDeleteView(DeleteView):
    model = ProteinCollection
    success_url = reverse_lazy('proteins:collections')

    def get_success_url(self):
        redirect_url = reverse_lazy('proteins:collections', kwargs={'owner': self.request.user})
        try:
            # check that this is an internal redirection
            resolve(redirect_url)
        except Exception:
            redirect_url = None
        return redirect_url or super().get_success_url()