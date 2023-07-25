from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_subject(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError(
                'Введите текст сообщения.')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_subject(self):
        data = self.cleaned_data['text']

        if data == '':
            raise forms.ValidationError(
                'Введите текст комментария.')
        return data
