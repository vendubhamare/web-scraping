# In[1]: 

# Importing required libraries

import csv
import time
from math import *
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# In[2]: 

# Visiting Career Guide Website

url1 = 'https://www.careerguide.com/career-options'

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.get(url1)
driver.implicitly_wait(5)


# In[3]: 

# Scraping all sub categories from the Career Guide website & storing them into sub_cats list

sub_cats = []

body = driver.find_element_by_class_name('c-body')
data = body.find_elements_by_tag_name('li')

for li in data:
    sub_cats.append(li.text.strip())


# In[4]:

# Opening CSV file for storing jobs data
csv_file = open('jobs_data.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Job Profile', 'Job URL', 'Company Name', 'Location'])


# In[5]:

# Looping through each sub category
for i in sub_cats:
    # For each sub category, creating the linkedin job search url for that sub category
    temp_url = f'https://www.linkedin.com/jobs/search?keywords={i}&location=India'
    driver.get(temp_url)
    driver.implicitly_wait(5)
    
    # Getting the count of total number of jobs present (of that sub category)
    # If we get error for getting the value of the count, then it means no jobs are available for that sub category
    try:
        count = driver.find_element_by_class_name('results-context-header__job-count').text
        count = count.replace(',','').replace('+','')
    except:
        continue
    # Counting the number of pages & scrolling the web page for that number of times (for getting all jobs)
    pages = int(ceil(int(count)/25))
    for i in range(pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
    
    jobs = driver.find_element_by_class_name('jobs-search__results-list').find_elements_by_tag_name('li')
    # Looping through each job present on the current web page
    for job in jobs:
        # Scraping the required fields of each job
        job_pos = job.find_element_by_class_name('base-search-card__title').text.strip()
        job_url = job.find_element_by_tag_name('a').get_attribute('href')
        company = job.find_element_by_class_name('base-search-card__subtitle').text.strip()
        location = job.find_element_by_class_name('job-search-card__location').text.strip()
        # Storing jobs data in csv file
        csv_writer.writerow([job_pos, job_url, company, location])


driver.close()
csv_file.close()








