#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt



def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere_info": hemi(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data



def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
            # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        news_p = slide_elem.find("div", class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p 


# ###Featured Images

def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url


def mars_facts():
    try:
        #mars facts
        #returns list of tables that encounter
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    #assign columns names
    df.columns=['description', 'Mars']

    #set index, updated index will remain in place without having to assign another variable
    df.set_index('description', inplace=True)

     #convert back to html
    return df.to_html(classes="table table-striped")



def hemi(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_names = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # Parse the HTML
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    #get the headings, headings is ok
    for heading in hemi_soup.find_all("h3"):
        hemisphere_names.append(heading.text.strip())
    print(hemisphere_names)


    # Search for thumbnail links
    results = hemi_soup.find_all('div', class_="collapsible results")
    thumb_results = results[0].find_all('a')
    thumb_links = []

    for thumbnail in thumb_results:
            #check for image
        if (thumbnail.img):
            # get attached links
            thumb_url = 'https://astrogeology.usgs.gov/' + thumbnail['href']
            
            # Append list with links
            thumb_links.append(thumb_url)

    #full images

    full_images = []

    for url in thumb_links:
            #browse to each link in the thumb_links list
        browser.visit(url)
            # Parse the data
        html = browser.html
        weather_soup = soup(html, 'html.parser')
            
            # Scrape each page 
        results = weather_soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']
            
            # full path
        img_link = 'https://astrogeology.usgs.gov/' + relative_img_path
            
            # Add full image links to a list
        full_images.append(img_link)


        # 4. Print the list that holds the dictionary of each image url and title.
        hemisphere_image_urls = []
        mars_zip = zip(hemisphere_names, full_images)

       # Iterate through zip
    for title, img in mars_zip:
            
        mars_dict = {}
            
            # Add hemisphere title to dictionary
        mars_dict['title'] = title
            
            # Add image url to dictionary
        mars_dict['img_url'] = img
            
            # Append the list with dictionaries
        hemisphere_image_urls.append(mars_dict)

    return hemisphere_image_urls








if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())



