import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import io
import base64
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

movies = pd.read_csv("movies_500.csv")
dataRating = "rating_500.txt"

data = []

# Proses setiap file
with open(dataRating, "r") as f:
        movie_id = None
        for line in f:
            line = line.strip()  # Hilangkan spasi di awal/akhir
            if line.endswith(":"):  # Jika baris adalah movie_id
                movie_id = int(line.replace(":", ""))  # Ambil movie_id
            else:  # Jika baris adalah data user_id, rating, timestamp
                user_id, rating, timestamp = line.split(",")
                data.append([movie_id, int(user_id), int(rating), timestamp])

# Konversi ke DataFrame
data_rating = pd.DataFrame(data, columns=["movie_id", "user_id", "rating", "timestamp"])

# Drop kolom timestamp (opsional, jika tidak diperlukan)
data_rating = data_rating.drop(columns=["timestamp"])

# melakukan merge dataset ratings dan movies
print("\n========MERGING========")
ratings = pd.merge(movies,data_rating)

# Pivot table menjadi format seperti yang diinginkan
user_ratings = ratings.pivot_table(index="user_id", columns="title", values="rating")

print("\n========COSINE SIMILARITY========")
cosine_sim_matrix = cosine_similarity(user_ratings.fillna(0).T)
cosine_sim_matrix = pd.DataFrame(cosine_sim_matrix, index=user_ratings.columns, columns=user_ratings.columns)

# Mencari movie mirip dengan "romantic_lover" list
print("\n========FIND SIMILAR COSINE========")

@app.route('/')
def landingpage():
    return render_template('landingpage.html')

@app.route('/result')
def recommending():
    movie_name = request.form.getlist("movie_name")
    rating = request.form.getlist("ratings")

     # Gabungkan menjadi tuple
    input = [(movie_name[i], int(rating[i])) for i in range(len(movie_name))]

    # Fungsi untuk mencari movie yang mirip
    def get_similar_cosine(movie_name, rating):
        similar_ratings = cosine_sim_matrix[movie_name] * rating
        similar_ratings = similar_ratings.sort_values(ascending=False)
        return similar_ratings

        similar_movies_cosine = pd.concat([get_similar_cosine(movie, rating) for movie, rating in input], axis=1)
        similar_movies = similar_movies_cosine.head(5).index.difference(movie for movie, rating in input)

if __name__ == '__main__':
    app.run(debug=True)