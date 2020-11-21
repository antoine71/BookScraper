import bookscraper as bs

book_url = 'http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html'
book = bs.Book(book_url)
book.export()