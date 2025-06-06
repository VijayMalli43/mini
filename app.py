from flask import Flask, request, render_template, redirect, url_for
from flask_cors import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)

# Load and preprocess data
try:
    df = pd.read_csv("Books_dataset.csv", encoding="unicode_escape")
    print("CSV Loaded Successfully.")
    print(df.columns)
    
    # Ensure required columns are present
    required_columns = ['title', 'author', 'description', 'keywords', 'rack']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Missing required columns in CSV")

    # Clean and standardize text data
    df = df.dropna(axis=1, how="all")
    for col in ['title', 'description', 'keywords', 'rack']:
        df[col] = df[col].astype(str).str.lower().str.strip()

    # Combine relevant columns for comprehensive search
    df['combined_text'] = df['title'] + ' ' + df['description'] + ' ' + df['keywords']

except Exception as e:
    print(f"Error loading CSV: {e}")
    df = None

# Load the SentenceTransformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
if df is not None:
    # Precompute embeddings for all book data
    df['combined_embedding'] = df['combined_text'].apply(lambda text: model.encode(text, convert_to_tensor=True))
    print("Embeddings Generated for Book Data.")

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('page1.html')

@app.route('/search', methods=['GET'])
def search_books():
    try:
        if df is None:
            raise ValueError("Book data is not available.")

        # Retrieve query and rack number from request
        query = request.args.get('query', '').strip().lower()
        rack_number = request.args.get('rack', '').strip().lower()
        print(f"Query received: '{query}', Rack Number: '{rack_number}'")

        # Start with all results
        results = df.copy()

        # Filter by rack number if specified
        if rack_number:
            results = results[results['rack'] == rack_number]
            if results.empty:
                print(f"No results found in rack '{rack_number}'.")
                return render_template('results.html', books=[], total_results=0)

        # Embed the user query and compute similarity only if query is provided
        if query:
            query_embedding = model.encode(query, convert_to_tensor=True)
            cosine_similarities = [util.pytorch_cos_sim(query_embedding, emb).item() for emb in results['combined_embedding']]

            # Add similarity scores to DataFrame and filter top matches
            results['similarity_score'] = cosine_similarities
            results = results[results['similarity_score'] > 0.3].sort_values(by='similarity_score', ascending=False).head(10)
        
        # Convert results to list format
        results_list = results.drop(columns=['combined_embedding', 'similarity_score'], errors='ignore').to_dict(orient='records')
        print(f"Results found: {len(results_list)}")

        return render_template('results.html', books=results_list, total_results=len(results_list))

    except Exception as e:
        print(f"Error during search: {e}")
        return render_template('results.html', books=[], total_results=0)

# book_data = {
#     'firstyear': ['Mathematics', 'Chemistry', 'Physics', 'C Programming', 'Python', 'English'],
#     'secondyear': ['Mathematics', 'Data Structures', 'Algorithms', 'English', 'Java', 'DBMS'],
#     'thirdyear': ['Programming', 'Web Technologies', 'English', 'OS', 'Software Engineering'],
#     'fourthyear': ['Web Technologies', 'Advanced Web Technology', 'Programming']
# }

@app.route('/category/<category>')
def category_books(category):
    books = df[df['year'] == category].to_dict(orient='records')  # Filter by 'year' column in your CSV
    
    title = f"{category.capitalize()} Books"  # Descriptive title for category
    return render_template('books.html', category=category.capitalize(), books=books, title=title)

@app.route('/year/<year>')
def year_books(year):
    df.columns = df.columns.str.strip().str.lower()  # Clean column headers

    if 'year' not in df.columns:
        return "The 'year' column is missing from the data.", 404

    # Filter books by the 'year' column
    filtered_books = df[df['year'].str.lower() == year.lower()]

    if filtered_books.empty:
        return render_template('books.html', year=year.capitalize(), books=[], title=f"No books found for {year.capitalize()}")

    books_list = filtered_books.to_dict(orient='records')
    
    # Pass a more descriptive title
    title = f"{year.capitalize()} Year Books"
    return render_template('books.html', year=year.capitalize(), books=books_list, title=title)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
