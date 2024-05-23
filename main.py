from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import time

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/dummy')
async def dummy():
    return { 'message': 'Justine Gwapo' }

@app.get('/api/getJobPostings')
async def getJobPostings():
    # STORE ONLINEJOBSPH IN A VARIABLE
    JOB_POSTING_URL = 'https://www.onlinejobs.ph/jobseekers/jobsearch'
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # THEN OPEN IN IT IN YOUR CHROME WEB BROWSER
    driver.get(JOB_POSTING_URL)

    # FIND JOBKEYWORD INPUT ELEMENT
    job_keyword_input = driver.find_element(By.ID, 'jobkeyword')
    # CLEAR THE INPUT ELEMENT OF ANY TEXT IT MAY HAVE
    job_keyword_input.clear()
    # SET THE VALUE FOR THE INPUT ELEMENT  (e.g., WEB DEVELOPER)
    job_keyword_input.send_keys('Web Developer')
    # SUBMIT THE JOB KEYWORD
    job_keyword_input.submit()

    job_titles = []
    job_types = []
    job_authors = []
    job_posted_dates = []
    job_budgets = []
    job_links = []
    
    # WEBDRIVERWAIT INSTANCE
    wait = WebDriverWait(driver, 1)

    # WAIT UNTIL THE RESULTS CONTAINER IS PRESENT
    results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'results')))

    # WAIT UNTIL JOB POST ELEMENTS ARE PRESENT INSIDE THE RESULTS CONTAINER
    job_posts = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.results .jobpost-cat-box')))

    # LIST OF WORDS TO REMOVE FROM THE TITLE
    # ALSO THE LIST OF WORDS THAT WE WILL ADD AS JOB TYPES
    words_to_remove = ["Any", "Part Time", "Full Time", "Gig"]

    # LOOP THRU THE JOB POSTS
    for job_post in job_posts:
        # FIND ELEMENT FOR THE JOB TITLE
        job_title = job_post.find_element(By.XPATH, './/h4[@data-original-title]')
        if len(job_title.text):
            cleaned_title = job_title.text
            # PROCESS FOR REMOVING THE JOB TYPE TEXT INSIDE JOB TITLE
            for word in words_to_remove:
                if cleaned_title.endswith(word):
                    # ASSIGN THE WORD AS THE JOB TYPE
                    job_types.append(word)
                    cleaned_title = cleaned_title[: -len(word)].strip()
                    break
        
            job_titles.append(cleaned_title)

        # FIND ELEMENT FOR JOB POSTED CONTAINER (CONTAINS AUTHOR & POSTING DATE INFO)
        job_posted_container = job_post.find_element(By.XPATH, './/p[@data-temp-2]')

        # SPLIT THE JOB POST CONTAINER TEXT WITH THE CHARACTER •
        job_posted_texts = job_posted_container.text.split('•')
        # STORE THE TEXTS WE JUST EXTRACTED
        job_authors.append(job_posted_texts[0].strip())
        job_posted = job_posted_texts[1].strip()
        job_posted_dates.append(job_posted[len('Posted On'): len(job_posted_texts[1])].strip())
        
        # FIND ELEMENT FOR JOB POSTED CONTAINER (CONTAINS AUTHOR & POSTING DATE INFO)
        job_budget = job_post.find_element(By.TAG_NAME, 'dd')
        job_budgets.append(job_budget.text if len(job_budget.text) else '??') 

        # FIND ELEMENT FOR JOB POST LINK
        job_link_element = job_post.find_element(By.TAG_NAME, 'a')
        job_link_element_value = job_link_element.get_attribute('href')
        
        # STORE THE JOB LINK
        job_links.append(job_link_element_value)

    # DELAY CLOSING OF BROWSER FOR X SECONDS/TIME
    time.sleep(5)
    # CLOSE THE BROWSER
    driver.quit()

    jobs = [
        {
            'job_title': title,
            'job_type': type_,
            'job_author': author,
            'job_posted_date': date,
            'job_budget': budget,
            'job_link': link
        }
        for title, type_, author, date, budget, link in zip(job_titles, job_types, job_authors, job_posted_dates, job_budgets, job_links)
    ]

    return { 'jobs': jobs }