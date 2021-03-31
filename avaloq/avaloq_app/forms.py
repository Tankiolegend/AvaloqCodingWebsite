from django import forms
from django.contrib.auth.forms import UserCreationForm
from avaloq_app.models import Question, Candidate
from django.contrib.auth.models import User

LANG_CHOICES = [
    ('java', 'Java'),
    ('python', 'Python'),
    ('javascript', 'Javascript'), ]


class CandidateForm(forms.ModelForm):
    forename = forms.CharField(max_length=50, help_text="Forename of candidate.")
    surname = forms.CharField(max_length=50, help_text="Surname of candidate.")
    questions = forms.ModelMultipleChoiceField(queryset=Question.objects.all(),
                                               widget=forms.CheckboxSelectMultiple(attrs={'class': 'single-checkbox'}),
                                               required=True)

    class Meta:
        model = Candidate
        fields = ('forename', 'surname', 'questions')


class CreateStaff(UserCreationForm):
    is_admin = forms.BooleanField(label="Admin", required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_admin')


class CodeForm(forms.Form):
    language = forms.CharField(label = "Language", widget=forms.Select(choices=LANG_CHOICES,  attrs={'id': 'language', 'onchange': "updateEditor()"}))

    code_text = forms.CharField(label="Code:", widget=forms.Textarea(attrs={'id': 'code_text', 'onchange':'submit()'}), required=False)

    user_test_input = forms.BooleanField(label="Test against custom input", required=False, initial=False, widget=forms.CheckboxInput(attrs={'id': 'user_test_input', 'class':'form-check-input','onchange':'valueChanged();'}))
    test_input = forms.CharField(label="TestInput:", required=False, widget=forms.Textarea(attrs={'id': 'test_input', }))
