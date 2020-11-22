# coding: utf-8

import csv
import re
import requests
from bs4 import BeautifulSoup


class Book:
    """this class defines a book as it can be found on http://books.toscrape.com/.
    It stores the following data:
        product_page_url
        universal_ product_code
        title
        price_including_tax
        price_excluding_tax
        number_available
        product_description
        category
        review_rating
        image_url

    The constructor takes an url of a book from http://books.toscrape.com as an attribute.
    It parses the html code, extract the data and store the store it in the object.
    The data can be accessed similarly as a dictionary (eg. book['title']).
    The object can be iterated similarly as a dictionary.
    """
    books_created = 0
    current_book = ''

    def __init__(self, book_url):
        """Class constructor:
            gets the url page and create an object BookSoup, inherited from BeautifulSoup
            extract the data using the methods defined in the class BookSoup
        """
        Book.books_created += 1
        Book.current_book = book_url
        book_soup = create_bookscraper_soup(book_url)

        self._book_data = {
            'product_page_url': book_url,
            'universal_product_code': book_soup.get_universal_product_code(),
            'title': book_soup.get_title(),
            'price_including_tax': book_soup.get_price_including_tax(),
            'price_excluding_tax': book_soup.get_price_excluding_tax(),
            'number_available': book_soup.get_number_available(),
            'product_description': book_soup.get_product_description(),
            'category': book_soup.get_category(),
            'review_rating': book_soup.get_review_rating(),
            'image_url': book_soup.get_image_url(),
        }

    def __getitem__(self, data):
        """Method that defines the accessor (same as a dictionary)"""
        return self._book_data[data]

    def __iter__(self):
        """Method that defines the iterator (same as a dictionary)"""
        return iter(self._book_data)

    def __str__(self):
        """Method that defines how the object is displayed on screen with the function print()"""
        representation = '--------------------------------------------------------------------\n'
        for attribute in self:
            representation = representation + attribute + ': ' + self[attribute] + '\n'
        return representation

    def export(self):
        """This method exports the object data in a csv file"""
        with open('results.csv', 'w', encoding='utf-8') as export_file:
            file_writer = csv.writer(export_file)
            file_writer.writerow([attribute for attribute in self])
            file_writer.writerow([self[attribute] for attribute in self])

class BookCategory:

    categories_total_number = 0
    categories_created = 0

    def __init__(self, category_name, category_url):
        BookCategory.categories_created += 1
        self.name = category_name
        print('[{}]\tParsing category {}...'.format(BookCategory.categories_created, self.name))
        soup_page = create_bookscraper_soup(category_url)
        self.books_urls = soup_page.get_books_urls(category_url)
        print('\t{} books found...'.format(len(self.books_urls)))
        self.books = [Book(url) for url in self.books_urls]
        print('\t{} books parsed...'.format(len(self.books)))

    def export(self, file_name):
        """This method exports the object data in a csv file"""
        csv_file_name = (file_name + '.csv').lower().replace(' ', '_')
        with open(csv_file_name, 'w', encoding='utf-8') as export_file:
            file_writer = csv.writer(export_file)
            file_writer.writerow([attribute for attribute in self.books[0]])
            for book in self.books:
                file_writer.writerow([book[attribute] for attribute in book])
        print('\tData for category {} exported as {}.'.format(file_name, csv_file_name))


class BookscraperSoup(BeautifulSoup):
    """This class inherits from the class BeautifulSoup and add methods for parsing the data required
    for the class Book:
        get_universal_ product_code
        get_title
        get_price_including_tax
        get_price_excluding_tax
        get_number_available
        get_product_description
        get_category
        get_review_rating
        get_image_url
    """

    def get_universal_product_code(self):
        """This method uses BeautifulSoup methods to retrieve the book's universal product code"""
        product_code = self.find('table', class_='table table-striped').find_all('td')[0].string
        return product_code

    def get_title(self):
        """This method uses BeautifulSoup methods to retrieve the book's title"""
        title = self.find(id='content_inner').find('h1').string
        return title

    def get_price_including_tax(self):
        """This method uses BeautifulSoup methods to retrieve the book's price excluding taxes"""
        price_inc_tax = self.find('table', class_='table table-striped').find_all('td')[3].string
        return price_inc_tax

    def get_price_excluding_tax(self):
        """This method uses BeautifulSoup methods to retrieve the book's price including taxes"""
        price_ex_tax = self.find('table', class_='table table-striped').find_all('td')[2].string
        return price_ex_tax

    def get_number_available(self):
        """This method uses BeautifulSoup methods to retrieve the quantity of books available"""
        availability_string = self.find('table', class_='table table-striped').find_all('td')[5].string
        # Since the previous expression returns a sentence, not only digits, we use a regex to check if
        # the book is in stock and extract the digits from the sentence
        if re.match(r'In stock', availability_string) is not None:
            number_available = re.search(r'\d+', availability_string).group()
        else:
            number_available = 0
        return number_available

    def get_product_description(self):
        """This method uses BeautifulSoup methods to retrieve the book's description"""
        # Since all the descriptions end by ' ...more' we cut the last 8 characters from the string
        try:
            product_description = self.find('div', id='product_description').next_sibling.next_sibling.string[:-8]
        except AttributeError:
            product_description = 'not available'
            print('WARNING - description missing for the following book: {}'.format(Book.current_book))
        return product_description

    def get_category(self):
        """This method uses BeautifulSoup methods to retrieve the book's category"""
        category = self.find('table', class_='table table-striped').find_all('td')[1].string
        return category

    def get_review_rating(self):
        """This method uses BeautifulSoup methods to retrieve the book's review rating"""
        ratings = {
            'star-rating One': '1',
            'star-rating Two': '2',
            'star-rating Three': '3',
            'star-rating Four': '4',
            'star-rating Five': '5'
        }
        for rating_class in ratings:
            if self.find('div', class_='col-sm-6 product_main').find('p', class_=rating_class) is not None:
                rating = ratings[rating_class]
                break
        return rating

    def get_image_url(self):
        """This method uses BeautifulSoup methods to retrieve the book's image url"""
        image_url_relative_path = self.find('div', class_='item active').find('img')['src']
        image_url = 'http://books.toscrape.com' + image_url_relative_path[5:]
        return image_url

    def get_books_urls(self, current_page_url):
        books_list = self.find('ol').find_all('li')
        books_urls_relative = [book.find('a')['href'] for book in books_list]
        books_urls = [url.replace('../../..', 'http://books.toscrape.com/catalogue') for url in books_urls_relative]
        if not self.is_last_page():
            next_page_url = self.get_next_page_url(current_page_url)
            next_page_soup = create_bookscraper_soup(next_page_url)
            books_urls.extend(next_page_soup.get_books_urls(next_page_url))
        return books_urls

    def get_next_page_url(self, current_page_url):
        next_page_url_file = self.find('li', class_='next').find('a')['href']
        next_page_url = swap_url_file(current_page_url, next_page_url_file)
        return next_page_url

    def is_last_page(self):
        if self.find('li', class_='next') is None:
            return True
        else:
            return False

def create_bookscraper_soup(url):
    req = requests.get(url)
    req.encoding = 'utf-8'
    bookscraper_soup = BookscraperSoup(req.text, 'html.parser')
    return bookscraper_soup

def swap_url_file(url, new_file):
    url_split = url.split('/')
    url_split[-1] = new_file
    new_url = '/'.join(url_split)
    return new_url

def get_all_categories():
    print('checking book categories...')
    front_page_url = 'http://books.toscrape.com/index.html'
    front_page_soup = create_bookscraper_soup(front_page_url)
    categories_list = front_page_soup.find('div', class_='side_categories').find('ul').find('ul').find_all('li')
    categories = []
    for item in categories_list:
        category_name = item.find('a').string.strip()
        url_relative = item.find('a')['href']
        category_url = 'http://books.toscrape.com/' + url_relative
        categories.append((category_name, category_url))
    print('{} categories found...'.format(len(categories)))
    return categories

