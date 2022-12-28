from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_subject(self):
        data = self.cleaned_data['subject']

        if data == '':
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data
