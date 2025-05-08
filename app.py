from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

# Load data
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_score = pickle.load(open('similarity_score.pkl', 'rb'))
final50 = pd.read_csv('final50.csv')

def recommend_books(book_name):
    index = np.where(pt.index == book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        temp_df = temp_df.drop_duplicates('Book-Title')
        item.extend(list(temp_df['Book-Title'].values))
        item.extend(list(temp_df['Image-URL-M'].values))
        item.extend(list(temp_df['Book-Author'].values))
        item.extend(list(temp_df['Year-Of-Publication'].values))
        data.append(item)

    return data

@app.route('/')
def home():
    books_data = final50.to_dict(orient='records')
    return render_template('index.html', books=books_data)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        try:
            data = recommend_books(user_input)
            return render_template('recommend.html', data=data, user_input=user_input)
        except:
            return render_template('recommend.html', data=None, user_input=user_input, not_found=True)
    return render_template('recommend.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    matches = [title for title in pt.index if search.lower() in title.lower()]
    return jsonify(matches[:10])

@app.route('/coming-soon')
def coming_soon():
    return render_template('coming_soon.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
