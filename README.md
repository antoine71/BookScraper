# BookScraper
This app scrapes all book from the website http://books.toscrape.com/ and extract the following data for each book:
        product_page_url,
        universal_ product_code,
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
The files are created in the current working directory. Existing files with the same name will be replaced. 


Operating instructions:

1. Install the python modules specified in the file requirement.txt
2. Navigate to the directory where you want the files to be saved
3. Run the python script script.py




