from selenium import webdriver 
import pandas as pd

# Script to Scrape page names from Harry Potter's Wiki.
# Will collect every page name, and save to hpwikia_pages.csv in this directory
# requires a chromedriver, or some other browser driver (in which case change code)

BASE_URL = "https://harrypotter.fandom.com/wiki/Special:AllPages"
EXTENSION = "?from="

def main():
    browser = webdriver.Chrome('./chromedriver')
    browser.get(BASE_URL)

    df = pd.DataFrame()
    last_element_text = None

    while True:
        try:
            page_list = []
            table = browser.find_element_by_class_name("mw-allpages-chunk")
            for element in table.find_elements_by_tag_name("li"):
                page_list.append(element.text)
            df = df.drop_duplicates(df.append(page_list))
            # It's slow to iteratively save the CSV, but it is good to save progress in case we timeout randomly.
            df.to_csv('hpwikia_pages.csv', header=None, index=False)
            browser.get(BASE_URL + EXTENSION + element.text)
            if element.text == last_element_text:
                print(f"Completed Scraping, found {len(df)} pages")
                break
            last_element_text = element.text
        except Exception as e:
            print(e)
            browser.close()
            break


if __name__ == '__main__':
    main()