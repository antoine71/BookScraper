# The module bookscraper contains all the custom classes and functions used for this project.
import bookscraper.bs_class as bs
import os
import platform

# We retrieve all the categories names and their corresponding url from the website http://books.toscrape.com/index.html
for category_name, category_url in bs.BookScraper('http://books.toscrape.com/').get_all_categories():
    # For each category, we create an object BookCollection.
    # The constructor of the class will generate a list of Book objects.
    # The Book objects contain the data to exported.
    book_collection = bs.BookCollection(category_name, category_url)
    # The method export_data is called to export the data of each Book object in a csv file.
    # The default export folder is ./csv/
    book_collection.export_data()
    # The method export_images is called to export the image of each Book object.
    # The default export folder is ./images/
    book_collection.export_images()
print('Scraping completed. Total: {} books scraped.'.format(bs.Book.books_created))

if platform.system() == 'Windows':
    os.system('pause')

