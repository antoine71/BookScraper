import bookscraper.bs_class as bs


def check_scraping_error(get_method):
    """ This function is a decorator that is intended to capture errors (missing data)
    while scraping data from a book page.

    It is intended to be used as a decorator for the methods of the class BookscraperSoup.

    It returns 'not available' instead of the data if the data is missing"""
    def modified_function(*parameters):
        try:
            return get_method(*parameters)
        except AttributeError:
            print('\tWARNING - failed to execute {} for the following book: {}'.format(get_method,
                                                                                       bs.Book.current_book))
            return 'not available'
    return modified_function

