import bookscraper as bs

categories = bs.get_all_categories()

for category in categories:
    category_books = bs.BookCategory(category[0], category[1])
    category_books.export(category[0])