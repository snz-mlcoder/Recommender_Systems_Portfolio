import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# --- 1. Load Dataset ---
try:
    movies = pd.read_csv('top10K-TMDB-movies.csv')
except FileNotFoundError:
    print("Error: 'dataset.csv' not found. Please make sure it is located in the root directory.")
    exit()

# --- 2. Feature Engineering ---
# Select relevant columns
movies = movies[['id', 'title', 'overview', 'genres']]

# Fill missing values with empty strings to avoid concatenation errors
movies['overview'] = movies['overview'].fillna("")
movies['genres'] = movies['genres'].fillna("")

# Create a 'tags' column by combining 'overview' and 'genres'
movies['tags'] = movies['overview'] + " " + movies['genres']

# Create a new DataFrame with essential columns for modeling
new_data = movies[['id', 'title', 'tags']]

# --- 3. Text Vectorization ---
# Convert text data into numerical vectors using CountVectorizer
cv = CountVectorizer(max_features=10000, stop_words='english')

# Apply fit_transform to the 'tags' column
vector = cv.fit_transform(new_data['tags'].values).toarray()

# --- 4. Compute Cosine Similarity ---
# Generate the cosine similarity matrix for movie vectors
similarity = cosine_similarity(vector)

# --- 5. Save Processed Data and Model Files ---
# Save movie data (as dictionary for easier serialization)
with open('movies_list.pkl', 'wb') as f:
    pickle.dump(new_data.to_dict(), f)

# Save similarity matrix
with open('similarity.pkl', 'wb') as f:
    pickle.dump(similarity, f)

print("Model preparation completed successfully. Files 'movies_list.pkl' and 'similarity.pkl' have been saved.")
