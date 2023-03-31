from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(label='Nom',max_length=25)
    email = forms.EmailField(label='E-mail de l\'expéditeur')
    to = forms.EmailField(label='E-mail du destinataire')
    comments = forms.CharField(label='Commentaires',required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model =Comment
        fields = ['name', 'email', 'body']