from django.views.generic import ListView
from django.db.models import Q
from apps.catalog.models import Category

class HomeView(ListView):
    model = Category
    template_name = 'core/home.html'
    context_object_name = 'categories'

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context
