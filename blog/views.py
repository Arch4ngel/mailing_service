from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from blog.models import Post
from pytils.translit import slugify
from django.contrib.auth.mixins import LoginRequiredMixin


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('title', 'body', 'image', 'is_published')
    success_url = reverse_lazy('blog:blog')
    extra_context = {
        'title': 'Новый пост'
    }

    def form_valid(self, form):
        if form.is_valid():
            new_post = form.save()
            new_post.slug = slugify(new_post.title)
            new_post.save()
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    extra_context = {'title': 'Блог'}

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        post.views_count += 1
        post.save()
        context['title'] = post.title
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ('title', 'body', 'image', 'is_published')
    extra_context = {'title': 'Редактировать пост'}

    def form_valid(self, form):
        if form.is_valid():
            new_post = form.save()
            new_post.slug = slugify(new_post.title)
            new_post.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:view', args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    extra_context = {'title': 'Удалить пост'}
    success_url = reverse_lazy('blog:blog')
