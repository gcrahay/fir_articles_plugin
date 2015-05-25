import datetime

from django.db import models
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from incidents.models import Incident, IncidentCategory
from fir_plugins.models import link_to

from fir_artifacts import artifacts
import fir_artifacts.models as artifacts_models


STATUS_CHOICES = (
	("O", "Open"),
	("A", "Archived"),
	("D", "Deleted"),
	)


@link_to(artifacts_models.File)
@link_to(artifacts_models.Artifact)
class Article(models.Model):
	date = models.DateTimeField(default=datetime.datetime.now, blank=True)
	subject = models.CharField(max_length=256)
	body = models.TextField()
	category = models.ForeignKey(IncidentCategory)
	incidents = models.ManyToManyField(Incident)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
	opened_by = models.ForeignKey(User)


	def __unicode__(self):
		return self.subject

	def is_open(self):
		return self.get_last_action != "Closed"


	def get_last_comment(self):
		return self.comments_set.order_by('-date')[0]


	def refresh_artifacts(self, data=""):
		if data == "":
			coms = self.comments_set.all()

			data = self.body
			for c in coms:
				data += "\n" + c.comment

		found_artifacts = artifacts.find(data)

		artifact_list = []
		for key in found_artifacts:
			for a in found_artifacts[key]:
				artifact_list.append((key, a))

		db_artifacts = artifacts_models.Artifact.objects.filter(value__in=[a[1] for a in artifact_list])

		exist = []

		for a in db_artifacts:
			exist.append((a.type, a.value))
			if self not in a.articles.all():
				a.articles.add(self)

		new_artifacts = list(set(artifact_list) - set(exist))
		all_artifacts = list(set(artifact_list))

		for a in new_artifacts:
			new = artifacts_models.Artifact(type=a[0], value=a[1])
			new.save()
			new.relations.add(self)

		for a in all_artifacts:
			artifacts.after_save(a[0], a[1], self)


	class Meta:
		permissions = (
			('access_articles', 'Can access articles'),
			('modify_articles', 'Can modify articles'),
		)


class ArticleComments(models.Model):
	date = models.DateTimeField(default=datetime.datetime.now, blank=True)
	comment = models.TextField()
	article = models.ForeignKey(Article, related_name="comments_set")
	opened_by = models.ForeignKey(User)

	def __unicode__(self):
		return u"Comment for article %s" % self.article.id


class ArticleAttribute(models.Model):
	name = models.CharField(max_length=50)
	value = models.CharField(max_length=200)
	article = models.ForeignKey(Article, related_name="attribute_set")

	def __unicode__(self):
		return "%s: %s" % (self.name, self.value)


class ArticleForm(ModelForm):

	def __init__(self, *args, **kwargs):
		super(ModelForm, self).__init__(*args, **kwargs)
		self.fields['subject'].error_messages['required'] = _('This field is required.')
		self.fields['category'].error_messages['required'] = _('This field is required.')

	class Meta:
		model = Article
		exclude = ('opened_by', 'incidents', 'artifacts')

class SearchArticleForm(forms.Form):
	category = forms.ModelChoiceField(label="Category", queryset=IncidentCategory.objects.all(),
                                      widget=forms.Select(attrs={'class':'form-control input-sm'}), required=False)
	status = forms.ChoiceField(choices=STATUS_CHOICES, initial=STATUS_CHOICES[0][0], required=False)


class ArticleCommentForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(ModelForm, self).__init__(*args, **kwargs)
		self.fields['comment'].error_messages['required'] = _('This field is required.')

	class Meta:
		model = ArticleComments
		exclude = ('article', 'opened_by')
		widgets = {
			'action': forms.Select(attrs={'required': True, 'class': 'form-control'})
		}