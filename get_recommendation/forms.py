from django import forms

class RatingForm(forms.Form):
    # Add your fields here, similar to your Tkinter entry fields
    anime1 = forms.CharField(label='Favorite Anime 1', max_length=100)
    rating1 = forms.IntegerField(label='Rating')
    anime2 = forms.CharField(label='Favorite Anime 2', max_length=100, required=False)
    rating2 = forms.IntegerField(label='Rating', required=False)
    anime3 = forms.CharField(label='Favorite Anime 3', max_length=100, required=False)
    rating3 = forms.IntegerField(label='Rating', required=False)
