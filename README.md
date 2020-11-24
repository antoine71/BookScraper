# BookScraper
This app scrapes all book from the website http://books.toscrape.com/ and extract the following data for each book:
        product_page_url,
        universal_product_code,
        title,
        price_including_tax,
        price_excluding_tax,
        number_available,
        product_description,
        category,
        review_rating,
        image_url.

The data are saved in csv files. One file is created for each category as per the classification of 
http://books.toscrape.com/
The csv files are created in a sub-folder ./csv/ 
The image corresponding to each book are saved in a subfolder ./images/
The image files are named as per the book universal product code.
Existing files with the same name will be replaced. 

Operating instructions:
1. install python3
2. Install the python modules specified in the file requirement.txt
3. Navigate to the directory where you want the files to be saved
4. Run the python script bookscraper/script.py




