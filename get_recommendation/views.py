from django.shortcuts import render
from .forms import RatingForm  
from .recommendation_logic import get_recommendations  
import pandas as pd
from django.http import JsonResponse
from django.urls import reverse


def home(request):
    form = RatingForm()
    return render(request, 'home.html', {'form': form})


# Function to load anime names from CSV
def load_anime_names():
    df = pd.read_csv('/Users/tanmaybhardwaj/Study/Anime_recommendation/get_recommendation/data/anime.csv') 
    return df['name'].tolist()  


def submit_ratings(request):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            recommendations = get_recommendations(request,form.cleaned_data)
            # Assuming you have a way to store recommendations temporarily
            request.session['recommendations'] = recommendations  # Storing in session as an example
            results_url = reverse('results')  # Make sure you have a 'results' named URL in your urls.py
            return JsonResponse({'results_url': results_url})
    else:
        form = RatingForm()
    return render(request, 'home.html', {'form': form})


# New view for anime autocomplete suggestions
def anime_titles(request):
    if 'term' in request.GET:
        names = load_anime_names()
        filtered_names = [name for name in names if request.GET.get('term').lower() in name.lower()]
        return JsonResponse(filtered_names, safe=False)
    return JsonResponse([])

def show_results(request):
    recommendations = request.session.get('recommendations', [])
    return render(request, 'results.html', {'recommendations': recommendations})

def progress_update(request):
    progress = request.session.get('progress', 0)
    return JsonResponse({'progress': progress})

