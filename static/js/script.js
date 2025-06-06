// Function to handle search by query and rack
function searchBooks() {
    const query = document.getElementById('searchQuery').value.trim();
    const rackNumber = document.getElementById('rackDropdown').value.trim();

    if (!query && !rackNumber) {
        alert('Please enter a search query or select a rack number.');
        return;  // Exit function if both query and rack are empty
    }

    console.log(`Searching for: ${query}, Rack Number: ${rackNumber}`);  // Debug statement
    showLoading();  // Display loading message

    let url = `http://127.0.0.1:5000/search?`;
    if (query) {
        url += `query=${encodeURIComponent(query)}`;
    }
    if (rackNumber) {
        url += `&rack=${encodeURIComponent(rackNumber)}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);  // Debug statement
            displayResults(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            displayError('An error occurred while fetching the data. Please try again later.');
        });
}

// Function to display search results
function displayResults(data) {
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.innerHTML = '';  // Clear previous results

    if (!data.books || data.total_results === 0) {
        resultContainer.innerHTML = '<p>No books found matching your query.</p>';
    } else {
        data.books.forEach(book => {
            const bookElement = document.createElement('div');
            bookElement.classList.add('book');
            bookElement.innerHTML = `
                <h2>${book.title}</h2>
                <p><strong>Author:</strong> ${book.author}</p>
                <p><strong>Description:</strong> ${book.description}</p>
                <p><strong>Keywords:</strong> ${book.keywords}</p>
                <p><strong>Rack:</strong> ${book.rack}</p>
                <hr>
            `;
            resultContainer.appendChild(bookElement);
        });
    }

    // Hide loading message after results are displayed
    hideLoading();
}

// Function to show a loading indicator
function showLoading() {
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.innerHTML = '<p>Loading results, please wait...</p>';
}

// Function to hide loading indicator
function hideLoading() {
    // Optionally, you can hide a loading indicator here
}

// Function to display error messages
function displayError(message) {
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.innerHTML = `<p class="error">${message}</p>`;
}
