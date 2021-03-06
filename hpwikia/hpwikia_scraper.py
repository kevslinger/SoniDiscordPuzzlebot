from selenium import webdriver 
import pandas as pd


browser = webdriver.Chrome('./chromedriver')

BASE_URL = "https://harrypotter.fandom.com/wiki/Special:AllPages"
EXTENSION = "?from="
last_element = None
browser.get(BASE_URL)

# Wait 20 seconds for page to load
timeout = 60


df = pd.DataFrame()

while True:
    try:
        page_list = []
        table = browser.find_element_by_class_name("mw-allpages-chunk")
        for element in table.find_elements_by_tag_name("li"):
            page_list.append(element.text)
        df = df.append(page_list)
        #df.to_csv('hpwikia_pages.csv', header=None, index=False)
        browser.get(BASE_URL + EXTENSION + element.text)
    except Exception as e:
        print(e)
        browser.close()
        break
print(page_list)

#except TimeoutException:
#    print("Timed out waiting for page to load")
#    browser.quit()