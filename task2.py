# In[1]: 

# Importing required libraries

import csv
import time
from math import *
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import mysql.connector as connector
import pandas as pd



# In[2]: 

# Visiting Career Guide Website

url1 = 'https://www.careerguide.com/career-options'

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.get(url1)
driver.implicitly_wait(5)



# In[3]: 

# Scraping all Categories & Sub-categories within them from the Career Guide website and 
# storing them into cats & sub_cats list respectively

cats = []
sub_cats = []

body = driver.find_element_by_class_name('c-body')
cols = body.find_elements_by_class_name('col-md-4')

for i in range(len(cols)):
    cat = cols[i].find_element_by_tag_name('a').text.strip()
    sub = cols[i].find_elements_by_tag_name('li')
    for i in range(len(sub)):
        cats.append(cat)
        sub_cats.append(sub[i].text.strip())



# In[4]:

# Creating connection with MySQL database

con = connector.connect(host = 'localhost',
                        port = '3306',
                        user = 'root',
                        password = '')

c = con.cursor(buffered=True)



# In[5]:

# Creating database -> jobs_data

query = "CREATE DATABASE jobs_data"
c.execute(query)

query = "USE jobs_data"
c.execute(query)

con.commit()



# In[6]:

# Creating required tables with necessary fields in jobs_data database

query = """CREATE TABLE jobs(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT , 
                            job_position VARCHAR(200) NOT NULL , 
                            apply_url VARCHAR(500) NOT NULL , 
                            company VARCHAR(50) NOT NULL , 
                            location VARCHAR(50) NOT NULL)"""
c.execute(query)

query = """CREATE TABLE company_details(c_id INT NOT NULL , 
                                        company_name VARCHAR(50) NOT NULL , 
                                        state VARCHAR(50) NOT NULL , 
                                        sub_category VARCHAR(50) NOT NULL, 
                                        FOREIGN KEY (c_id) REFERENCES jobs(id))"""
c.execute(query)

query = """CREATE TABLE states(s_id INT NOT NULL , 
                            state VARCHAR(50) NOT NULL, 
                            FOREIGN KEY (s_id) REFERENCES jobs(id))"""
c.execute(query)

query = """CREATE TABLE job_types_1(cat_id INT NOT NULL , 
                                    category VARCHAR(50) NOT NULL, 
                                    FOREIGN KEY (cat_id) REFERENCES jobs(id))"""
c.execute(query)

query = """CREATE TABLE job_types_2(sc_id INT NOT NULL , 
                                    sub_category VARCHAR(50) NOT NULL, 
                                    FOREIGN KEY (sc_id) REFERENCES jobs(id))"""
c.execute(query)

con.commit()



# In[7]: Scraping jobs data and storing them into the database

# Looping through each sub category
for i in range(len(sub_cats)):
    print(i)
    # For each sub category, creating the linkedin job search url for that sub category
    temp_url = f'https://www.linkedin.com/jobs/search?keywords={sub_cats[i]}&location=India'
    driver.get(temp_url)
    driver.implicitly_wait(5)
    
    # Getting the count of total number of jobs present (of that sub category)
    # If we get error for getting the value of the count, then it means no jobs are available for that sub category
    try:
        count = driver.find_element_by_class_name('results-context-header__job-count').text.strip()
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
        try:
            job_pos = job.find_element_by_class_name('base-search-card__title').text.strip()
            job_url = job.find_element_by_tag_name('a').get_attribute('href')
            company = job.find_element_by_class_name('base-search-card__subtitle').text.strip()
            location = job.find_element_by_class_name('job-search-card__location').text.strip()
        except:
            continue
        
        # Storing jobs data in MySQL database
        try:
            # jobs table
            query = """
                INSERT INTO jobs(job_position, apply_url, company, location)
                VALUES("%s", "%s", "%s", "%s")
            """ %(job_pos, job_url, company, location)
            c.execute(query)
            con.commit()

            # Fetching job id (primary key) of the stored job
            query = '''SELECT id FROM jobs WHERE apply_url="%s"''' %(job_url)
            c.execute(query)
            job_id = c.fetchone()[0]

            # company table
            state = location.split(', ')[1].strip()
            query = """
                INSERT INTO company_details(c_id, company_name, state, sub_category)
                VALUES(%s, "%s", "%s", "%s")
            """ %(job_id, company, state, sub_cats[i])
            c.execute(query)
            con.commit()

            # states table
            query = """
                INSERT INTO states(s_id, state)
                VALUES(%s, "%s")
            """ %(job_id, state)
            c.execute(query)
            con.commit()

            # job_types_1 (Categories) table
            query = """
                INSERT INTO job_types_1(cat_id, category)
                VALUES(%s, "%s")
            """ %(job_id, cats[i])
            c.execute(query)
            con.commit()
            
            # job_types_2 (Sub-Categories) table
            query = """
                INSERT INTO job_types_2(sc_id, sub_category)
                VALUES(%s, "%s")
            """ %(job_id, sub_cats[i])
            c.execute(query)
            con.commit()
            
            time.sleep(0.5)

        except TimeoutError as e:
            con = connector.connect(host = 'localhost',
                                    port = '3308',
                                    user = 'root',
                                    password = '',
                                    database = 'jobs_data')
            c = con.cursor(buffered=True)
            continue

        except Exception as e:
            continue



con.close()
driver.close()

















