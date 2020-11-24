# coding: utf-8

import csv
import os
import re
import requests
from bs4 import BeautifulSoup


def check_scraping_error(get_function):
    """ This function is a decorator that is intended to capture errors (missing data)
    while scraping data from a book page. It returns 'not available' instead of the data
    if the data is missing"""
    def modified_function(*parameters):
        try:
            return get_function(*parameters)
        except AttributeError:
            print('\tWARNING - failed to execute {} for the following book: {}'.format(get_function, Book.current_book))
            return 'not available'
    return modified_function


def create_request(url):
    """This function creates an http request and returns a request response object.
    If the status code of the response is more than 400, it raises an exception and interrupts the program"""
    r = requests.get(url)
    if r.ok:
        return r
    else:
        raise Exception('ERROR - http status code {} - Failed to retrieve the following page: {}'
                        .format(r.status_code, url))


def create_bookscraper_soup(url):
    """This function creates and return a BookscraperSoup object from an url"""
    r = create_request(url)
    r.encoding = 'utf-8'
    bookscraper_soup = BookscraperSoup(r.text, 'html.parser')
    return bookscraper_soup


def swap_url_file(url, new_file):
    """This function changes the file name at the end of an url (eg. index.html changed to page2.html)"""
    url_split = url.split('/')
    url_split[-1] = new_file
    new_url = '/'.join(url_split)
    return new_url


def get_all_categories():
    """This method returns the list of all the categories displayed on the website
    http://books.toscrape.com/index.html"""
    print('checking book categories...')
    front_page_url = 'http://books.toscrape.com/index.html'
    front_page_soup = create_bookscraper_soup(front_page_url)
    categories_list = front_page_soup.find('div', class_='side_categories').find('ul').find('ul').find_all('li')
    categories = []
    for item in categories_list:
        category_name = item.find('a').string.strip()
        url_relative = item.find('a')['href']
        category_url = 'http://books.toscrape.com/' + url_relative
        categories.append({'name': category_name, 'url': category_url})
    print('{} categories found...'.format(len(categories)))
    return categories


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
    The data is stored in a dictionary.
    It includes a method export_image that downloads the image file of the book.
    """

    books_created = 0
    current_book = ''
    headers = [
        'product_page_url',
        'universal_product_code',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url',
    ]

    def __init__(self, book_url):
        """Class constructor:
            gets the url page and create an object BookSoup, inherited from BeautifulSoup
            extract the data using the methods defined in the class BookSoup. \
            The data is stored in a dictionary.
        """
        Book.books_created += 1
        Book.current_book = book_url
        book_soup = create_bookscraper_soup(book_url)

        self.data = {
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

    def export_image(self, folder):
        """This method download and save the image the of book"""
        file_name = self.data['universal_product_code'] + '.jpg'
        file_path = folder + file_name
        r = create_request(self.data['image_url'])
        with open(file_path, 'wb') as file:
            file.write(r.content)


class BookCollection:
    """this class contains a list of Book objects that belong to a category:
    It includes a method to export the books data in a csv file and to export the books images files.
    """
    collections_created = 0

    def __init__(self, category_name, category_url):
        BookCollection.collections_created += 1
        book_collection_soup = create_bookscraper_soup(category_url)

        self.name = category_name
        print('[{}]\tParsing category {}...'.format(BookCollection.collections_created, self.name))

        self.books_urls = book_collection_soup.get_books_urls(category_url)
        print('\t{} books found...'.format(len(self.books_urls)))

        self.books = [Book(url) for url in self.books_urls]
        print('\t{} books parsed...'.format(len(self.books)))

    def export_data(self, folder='csv/'):
        """This method exports the object data in a csv file in a subdirectory"""
        file_name = (self.name + '.csv').lower().replace(' ', '_')
        file_path = folder + file_name
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
        with open(file_path, 'w', encoding='utf-8') as export_file:
            file_writer = csv.writer(export_file)
            file_writer.writerow(Book.headers)
            for book in self.books:
                file_writer.writerow(book.data.values())
        print('\tData for category {} exported as {}/{}.'.format(self.name, os.getcwd(), file_path))

    def export_images(self, folder='images/'):
        """This method exports the images files in a csv subdirectory"""
        print('\tDownloading images...')
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
        images_counter = 0
        for book in self.books:
            book.export_image(folder)
            images_counter += 1
        print('\t{} images saved in folder {}/{}'.format(images_counter, os.getcwd(), folder))


class BookscraperSoup(BeautifulSoup):
    """This class inherits from the class BeautifulSoup and add methods for parsing the data required
    for the classes Book and BookCategory:
        get_universal_ product_code
        get_title
        get_price_including_tax
        get_price_excluding_tax
        get_number_available
        get_product_description
        get_category
        get_review_rating
        get_image_url
        get_books_url
        get_books_urls
        get_next_page_url
        is_last_page
    """

    @check_scraping_error
    def get_universal_product_code(self):
        """This method uses BeautifulSoup methods to retrieve the book's universal product code"""
        product_code = self.find('table', class_='table table-striped').find_all('td')[0].string
        return product_code

    @check_scraping_error
    def get_title(self):
        """This method uses BeautifulSoup methods to retrieve the book's title"""
        title = self.find(id='content_inner').find('h1').string
        return title

    @check_scraping_error
    def get_price_including_tax(self):
        """This method uses BeautifulSoup methods to retrieve the book's price excluding taxes"""
        price_inc_tax = self.find('table', class_='table table-striped').find_all('td')[3].string
        return price_inc_tax

    @check_scraping_error
    def get_price_excluding_tax(self):
        """This method uses BeautifulSoup methods to retrieve the book's price including taxes"""
        price_ex_tax = self.find('table', class_='table table-striped').find_all('td')[2].string
        return price_ex_tax

    @check_scraping_error
    def get_number_available(self):
        """This method uses BeautifulSoup methods to retrieve the quantity of books available"""
        availability_string = self.find('table', class_='table table-striped').find_all('td')[5].string
        # Since the previous expression returns a sentence, not only digits, we use a regex to check if
        # the book is in stock and extract the digits from the sentence
        if re.match(r'In stock', availability_string) is not None:
            number_available = re.search(r'\d+', availability_string).group()
        else:
            number_available = '0'
        return number_available

    @check_scraping_error
    def get_product_description(self):
        """This method uses BeautifulSoup methods to retrieve the book's description"""
        # Since all the descriptions end by ' ...more' we cut the last 8 characters from the string
        product_description = self.find('div', id='product_description').next_sibling.next_sibling.string[:-8]
        return product_description

    @check_scraping_error
    def get_category(self):
        """This method uses BeautifulSoup methods to retrieve the book's category"""
        category = self.find('table', class_='table table-striped').find_all('td')[1].string
        return category

    @check_scraping_error
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

    @check_scraping_error
    def get_image_url(self):
        """This method uses BeautifulSoup methods to retrieve the book's image url"""
        image_url_relative_path = self.find('div', class_='item active').find('img')['src']
        image_url = 'http://books.toscrape.com' + image_url_relative_path[5:]
        return image_url

    def get_books_urls(self, current_page_url):
        """This method uses BeautifulSoup methods to return the list of url af all books in a given category
        It is called recursively until all the pages of the category are scraped"""
        books_list = self.find('ol').find_all('li')
        books_urls_relative = [book.find('a')['href'] for book in books_list]
        books_urls = [url.replace('../../..', 'http://books.toscrape.com/catalogue') for url in books_urls_relative]
        if not self.is_last_page():
            next_page_url = self.get_next_page_url(current_page_url)
            next_page_soup = create_bookscraper_soup(next_page_url)
            books_urls.extend(next_page_soup.get_books_urls(next_page_url))
        return books_urls

    def get_next_page_url(self, current_page_url):
        """This method returns the url of the next page of the category
        (if the books are displayed in more than one page)"""
        next_page_url_file = self.find('li', class_='next').find('a')['href']
        next_page_url = swap_url_file(current_page_url, next_page_url_file)
        return next_page_url

    def is_last_page(self):
        """This method checks if the current category page is the last page of the category and returns a boolean"""
        if self.find('li', class_='next') is None:
            return True
        else:
            return False




