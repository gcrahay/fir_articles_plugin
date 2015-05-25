# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseServerError
from json import dumps
from django.core import serializers

from fir_articles.models import Article, ArticleCommentForm, ArticleAttribute, ArticleComments, \
	ArticleForm, SearchArticleForm

from fir_artifacts.artifacts import all_for_object
from incidents.models import ValidAttribute


@login_required
@permission_required(['fir_articles.access_articles', 'fir_articles.modify_articles'])
def details(request, article_id):
	a = get_object_or_404(Article, pk=article_id)

	form = ArticleCommentForm()

	(artifacts, artifacts_count, correlated_count) = all_for_object(a)

	valid_attributes = a.category.validattribute_set.all()
	attributes = a.attribute_set.all()

	comments = a.comments_set.all().order_by('date')

	return render(request, "fir_articles/detail-all.html", {"article": a,
															"comment_form": form,
															'correlated_count': correlated_count,
															'artifacts_count': artifacts_count,
															'artifacts': artifacts,
															'attributes': attributes,
															'valid_attributes': valid_attributes,
															'comments': comments
															})


@login_required
@permission_required('fir_articles.modify_articles')
def change_status(request, article_id, status):
	article = get_object_or_404(Article, pk=article_id)
	article.status = status
	article.save()

	status_name = 'Closed'
	if status == 'O':
		status_name = 'Opened'
	elif status == 'A':
		status_name = 'Archived'

	comment = ArticleComments()
	comment.comment = "Status changed to '%s'" % status_name
	comment.date = datetime.datetime.now()
	comment.article = article
	comment.opened_by = request.user
	comment.save()

	return redirect("articles:details", article_id=article.id)


@login_required
@permission_required('fir_articles.modify_articles')
def new_article(request):
	if request.method == 'POST':
		form = ArticleForm(request.POST)
		form.status = 'Open'
		print form.errors
		if form.is_valid():
			article = form.save(commit=False)

			comment = ArticleComments()
			comment.comment = "Article opened"
			article.opened_by = request.user
			article.save()
			form.save_m2m()
			comment.article = article
			comment.opened_by = request.user
			comment.date = article.date
			comment.save()

			article.refresh_artifacts(article.body)

			return redirect("articles:details", article_id=article.id)

	else:
		form = ArticleForm()

	return render(request, 'fir_articles/new.html', {'form': form, 'mode': 'new'})


def diff(article, form):
	comments = []
	for i in form:
		# skip the following fields from diff
		if i in ['body', ]:
			continue

		new = form[i]
		old = getattr(article, i)

		if new != old:

			label = i

			if old == "O": old = 'Open'
			if old == "A": old = 'Archived'
			if old == "D": old = 'Deleted'
			if new == "O": new = 'Open'
			if new == "A": new = 'Archived'
			if new == "D": new = 'Deleted'

			comments.append(u'Changed "%s" from "%s" to "%s";' % (label, old, new))

	return "\n".join(comments)


@login_required
@permission_required('fir_articles.modify_articles')
def edit_article(request, article_id):
	article = get_object_or_404(Article, pk=article_id)

	if request.method == "POST":
		form = ArticleForm(request.POST, instance=article)

		if form.is_valid():
			extra_comments = diff(Article.objects.get(pk=article_id), form.cleaned_data)
			if extra_comments != "":
				comment = ArticleComments()
				comment.comment = extra_comments
				comment.article = article
				comment.opened_by = request.user
				comment.save()

			form.save()
			article.refresh_artifacts(article.body)
			article.save()

			return redirect("articles:details", article_id=article.id)
	else:
		form = ArticleForm(instance=article)

	return render(request, 'fir_articles/new.html', {'article': article, 'form': form, 'mode': 'edit'})


@login_required
@permission_required(['fir_articles.access_articles', 'fir_articles.modify_articles'])
def list_articles(request):
	found_entries = Article.objects.all()
	if request.method == "POST":
		form = SearchArticleForm(request.POST)
		if form.is_valid():
			category = form.cleaned_data['category']
			status = form.cleaned_data['status']
			if category != '' and category is not None:
				found_entries = found_entries.filter(category=category)
			if status != '' and status is not None:
				found_entries = found_entries.filter(status=status)
		page = request.POST.get('page')
	else:
		form = SearchArticleForm()
		found_entries = found_entries.filter(status='O')
		page = request.GET.get('page')

	incident_number = request.user.profile.incident_number

	p = Paginator(found_entries, incident_number)

	try:
		found_entries = p.page(page)
	except PageNotAnInteger:
		found_entries = p.page(1)
	except EmptyPage:
		found_entries = p.page(1)
	return render(request, 'fir_articles/list.html', {'form': form, 'articles': found_entries})


# attributes ================================================================

@login_required
@permission_required('fir_articles.modify_articles')
def add_attribute(request, article_id):
	article = get_object_or_404(Article, pk=article_id)
	if request.method == "POST":
		# First, check if it is a valid attribute
		valid_attribute = get_object_or_404(ValidAttribute, name=request.POST['name'])

		# Create a new attribute
		a = ArticleAttribute(name=valid_attribute.name, value=request.POST['value'])
		# Except if valid attribute has an unit and this particular attribute already exists
		# In this case, a single attribute should be keeped, with an updated value
		if valid_attribute.unit is not None and valid_attribute.unit != "":
			try:
				a = article.attribute_set.get(name=valid_attribute.name)
				a.value = str(int(a.value) + int(request.POST['value']))
			except:
				pass

		a.article = article
		a.save()

		if request.is_ajax():
			return render(request, 'fir_articles/_attributes.html', {'attributes': article.attribute_set.all(),
																	 'article': article})

	return redirect('incidents:details', incident_id=article_id)


@login_required
@permission_required('fir_articles.modify_articles')
def delete_attribute(request, article_id, attribute_id):
	a = get_object_or_404(ArticleAttribute, pk=attribute_id)
	if request.method == "POST":
		a.delete()
	return redirect('articles:details', article_id=article_id)


# comments ==================================================================

@login_required
@permission_required(['fir_articles.access_articles', 'fir_articles.modify_articles'])
def edit_comment(request, article_id, comment_id):
	c = get_object_or_404(ArticleComments, pk=comment_id, incident_id=article_id)
	if request.method == "POST":
		form = ArticleCommentForm(request.POST, instance=c)
		if form.is_valid():
			form.save()
			return redirect("articles:details", article_id=c.article_id)
	else:
		form = ArticleCommentForm(instance=c)

	return render(request, 'fir_articles/edit_comment.html', {'c': c, 'form': form})


@login_required
@permission_required('fir_articles.modify_articles')
def delete_comment(request, article_id, comment_id):
	if request.method == "POST":
		c = get_object_or_404(ArticleComments, pk=comment_id, article_id=article_id)
		msg = "Comment '%s' deleted." % (c.comment[:20] + "...")
		c.delete()
		return redirect('articles:details', article_id=c.article_id)
	else:
		return redirect('articles:details', article_id=c.article_id)


@login_required
@permission_required('fir_articles.modify_articles')
def update_comment(request, comment_id=None):
	if comment_id is None:
		ret = {'status': 'error', 'errors': ['Unknown comment', ]}
		return HttpResponseServerError(dumps(ret), content_type="application/json")
	if request.method == 'GET':
		c = [get_object_or_404(ArticleComments, pk=comment_id)]
		serialized = serializers.serialize('json', c)
		return HttpResponse(dumps(serialized), content_type="application/json")
	else:
		c = get_object_or_404(ArticleComments, pk=comment_id)
		comment_form = ArticleCommentForm(request.POST, instance=c)

		if comment_form.is_valid():

			c = comment_form.save()

			a = get_object_or_404(Article, pk=c.article.id)
			a.refresh_artifacts(c.comment)

			return render(request, 'fir_articles/_comment.html', {'comment': c, 'article': a})
		else:
			ret = {'status': 'error', 'errors': comment_form.errors}
			return HttpResponseServerError(dumps(ret), content_type="application/json")


@login_required
@permission_required('fir_articles.access_articles')
def comment(request, article_id):
	i = get_object_or_404(Article, pk=article_id)

	if request.method == "POST":
		comment_form = ArticleCommentForm(request.POST)
		if comment_form.is_valid():
			com = comment_form.save(commit=False)
			com.article = i
			com.opened_by = request.user
			com.save()
			i.refresh_artifacts(com.comment)

			return render(request, 'fir_articles/_comment.html', {'article': i, 'comment': com})
		else:
			ret = {'status': 'error', 'errors': comment_form.errors}
			return HttpResponseServerError(dumps(ret), content_type="application/json")

	return redirect('incidents:details', article_id=article_id)
