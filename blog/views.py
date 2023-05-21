from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

# from django.views.generic import ListView




# class PostListView(ListView):
#     """
#     Alternative post list view
#     """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Pagiantion with 3 post per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)

    except EmptyPage:
        # if page_number is out of range deliver Last page of results
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts':posts,
        'tag':tag
    }
    return render(request, 'blog/post/list.html',context)


def post_detail(request, year, month, day, post,tag_slug=None):

    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
      

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    # Form for users to comment
    form = CommentForm()

    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    context = {
        'post':post,
        'comments':comments,
        'form':form,
        'similar_posts':similar_posts,
        'tag':tag
    }

    return render(request, 'blog/post/detail.html',context)


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            datas = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{datas['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"le commentaire de {datas['name']} : {datas['comments']}"
            send_mail(subject, message, datas['email'], [datas['to']])
            sent = True

    else:
        form = EmailPostForm()

    context = {
        'post':post,
        'form':form,
        'sent':sent
    }
    return render(request, 'blog/post/share.html',context)
    


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
        context = {
            'post':post,
            'form':form,
            'comment': comment
        }
    return render(request, 'blog/post/comment.html',context)

# Building a search view (Version 1)
# def post_search(request):
#        form = SearchForm()
#        query = None
#        results = []
#        if 'query' in request.GET:
#            form = SearchForm(request.GET)
#            if form.is_valid():
#                query = form.cleaned_data['query']
#                results = Post.published.annotate(
#                    search=SearchVector('title', 'body'),
#                ).filter(search=query)
#        return render(request,
#                      'blog/post/search.html',
#                      {'form': form,
#                       'query': query,
#                       'results': results})



# # Stemming and ranking results (Version 2)
# '''
# Stemming is the process of reducing words to their word stem, base, or root form. 
# Stemming is used by search engines to reduce indexed words to their stem, and to 
# be able to match inflected or derived words. For example, the words “music”, “musical” 
# and “musicality” can be considered similar words by a search engine
# '''
# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []

#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_vector = SearchVector('title', 'body')
#             search_query = SearchQuery(query)
#             results = Post.published.annotate(
#                 search=search_vector,
#                 rank=SearchRank(search_vector, search_query),
#             ).filter(search=search_query).order_by('-rank')

    
#     context = {
#         'form':form,
#         'query':query,
#         'results': results
#     }
#     return render(request,'blog/post/search.html', context)




# # Stemming and removing stop words in different languages (Version 3)
# '''
# We can set up SearchVector and SearchQuery to execute stemming and remove stop words in any language. 
# We can pass a config attribute to SearchVector and SearchQuery to use a different search configuration. 
# This allows us to use different language parsers and dictionaries.
# The following example executes stemming and removes stops in Spanish:
# '''
# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []

#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             search_vector = SearchVector('title', 'body', config='spanish')
#             search_query = SearchQuery(query, config='spanish')
#             results = Post.published.annotate(
#                 search=search_vector,
#                 rank=SearchRank(search_vector, search_query),
#             ).filter(search=search_query).order_by('-rank')

    
#     context = {
#         'form':form,
#         'query':query,
#         'results': results
#     }
#     return render(request,'blog/post/search.html', context)




# Searching with trigram similarity (Version 4)
'''
Another search approach is trigram similarity. A trigram is a group of three consecutive characters.
You can measure the similarity of two strings by counting the number of trigrams that they share.
This approach turns out to be very effective for measuring the similarity of words in many languages.

To use trigrams in PostgreSQL, you will need to install the pg_trgm extension first. 
Execute the fol- lowing command in the shell prompt to connect to your database:

1) psql blog  

Then, execute the following command to install the pg_trgm extension:

2) CREATE EXTENSION pg_trgm;

You will get the following output:

3) CREATE EXTENSION

'''
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
    
    context = {
        'form':form,
        'query':query,
        'results': results
    }
    return render(request,'blog/post/search.html', context)

