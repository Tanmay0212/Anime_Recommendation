import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise.model_selection import train_test_split
import boto3
from io import StringIO
import os


ANIME_FILE_PATH = '/Users/tanmaybhardwaj/Study/Anime_recommendation/get_recommendation/data/anime.csv'
RATING_FILE_PATH = '/Users/tanmaybhardwaj/Study/Anime_recommendation/get_recommendation/data/rating.csv'

def preprocess_data():
    print("In preprocess function")
    """Loads and preprocesses the anime and rating data."""
    
    session = boto3.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    s3 = session.resource('s3')

    # Your bucket and file names
    bucket_name = 'aws-animebucket'
    file_name1 = 'rating.csv'
    file_name2 = 'anime.csv'
    print("fetching data from S3 bucket..")
    # Get the object from the bucket
    obj1 = s3.Object(bucket_name, file_name1)
    obj2 = s3.Object(bucket_name, file_name2)
    response1 = obj1.get()
    response2 = obj2.get()
    file_content1 = response1['Body'].read().decode('utf-8')
    file_content2 = response2['Body'].read().decode('utf-8')
    # Use pandas to convert the CSV to a DataFrame
    csv_data1 = StringIO(file_content1)
    csv_data2 = StringIO(file_content2)
    rating_df = pd.read_csv(csv_data1)
    anime_df = pd.read_csv(csv_data2)
    
    #anime_df = pd.read_csv(ANIME_FILE_PATH)
    #rating_df = pd.read_csv(RATING_FILE_PATH)
    rating_df = rating_df.replace({-1: float('nan')})  # Replace -1 with NaN
    return anime_df, rating_df

def get_recommendations(request,form_data):
    print("In Get recommendation function")
    request.session['progress'] = 10
    anime_df, rating_df = preprocess_data()
    anime_list = []
    rating_list = []
    for i in range(1, 4):
        anime_list.append(form_data.get(f'anime{i}', None))
        rating_list.append(form_data.get(f'rating{i}', None))
    request.session['progress'] = 20

    user_id = rating_df['user_id'].max() + 1
    anime_input = anime_df[anime_df['name'].isin(anime_list)].reset_index(drop=True)
    user_ratings = pd.DataFrame({'user_id': [user_id]*len(anime_input), 'anime_id': anime_input['anime_id'], 'rating': [float(rating) for rating in rating_list[:len(anime_input)]]})
    rating_df = pd.concat([rating_df, user_ratings], ignore_index=True)

    request.session['progress'] = 30
    rating_df['rating'] = rating_df['rating'].fillna(0)
    rating_df['rating'] = rating_df.groupby('user_id')['rating'].transform(lambda x: x.replace(0, x.mean()).astype(int))
    request.session['progress'] = 40

    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(rating_df[['user_id', 'anime_id', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.25)
    request.session['progress'] = 70
    print("Model is Running...")
    model = SVD()
    model.fit(trainset)
    print("Model Running completed!")
    request.session['progress'] = 80
    anime_ids = [anime_id for anime_id in rating_df['anime_id'].unique() if anime_id not in anime_input['anime_id'].unique()]

    predictions = sorted([model.predict(user_id, anime_id) for anime_id in anime_ids], key=lambda x: x.est, reverse=True)

    anime_name=[]
    request.session['progress'] = 90
    for i in range(10):
        anime_id = predictions[i].iid
        anime_name.append(anime_df[anime_df['anime_id'] == anime_id]['name'].values[0])
    request.session['progress'] = 100
    return anime_name


