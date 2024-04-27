##Assignment 4 question 5
#parser.py
#This program parses the HTML content of a webpage retrieved from a MongoDB collection and extracts information about faculty members

from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup

def debug_print(message):
    print(f"[DEBUG] {message}")

# Establishing connection to the MongoDB server
client = MongoClient('localhost', 27017)
debug_print("Connected to MongoDB.")

db = client['cs_crawler']
pages_collection = db['pages']
professors_collection = db['professors']
debug_print("Database and collection selected.")

# Fetches the HTML content of the Permanent Faculty page from MongoDB
faculty_page_url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'
faculty_page = pages_collection.find_one({'url': faculty_page_url})
debug_print(f"Searching for URL in database: {faculty_page_url}")

# Check if the page was found and parse its content
if faculty_page:
    html_content = faculty_page['html'].decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    debug_print("Permanent Faculty page HTML content retrieved.")

    # Find the container holding the faculty members information
    faculty_containers = soup.select('div.clearfix')
    debug_print(f"Found {len(faculty_containers)} faculty member containers.")

    # Extract and process each faculty member's information
    for container in faculty_containers:
        h2_element = container.find('h2')
        if h2_element:
            name = h2_element.get_text(strip=True)
        else:
            debug_print("No h2 element found in this container.")
            continue

        title = office = phone = email = web = ""

        p_element = container.find('p')
        if p_element:
            strong_tags = p_element.find_all('strong')
            for strong_tag in strong_tags:
                category = strong_tag.get_text(strip=True).lower()
                info = strong_tag.next_sibling
                if info and isinstance(info, str):
                    info = info.strip().lstrip(':').strip()  

                if 'title:' in category or 'title' in category:
                    title = info
                elif 'office:' in category or 'office' in category:
                    office = info
                elif 'phone:' in category or 'phone' in category:
                    phone = info
                elif 'email:' in category or 'email' in category:
                    email_tag = strong_tag.find_next_sibling('a')
                    if email_tag and email_tag.has_attr('href'):
                        email = email_tag['href'].replace('mailto:', '')
                elif 'web:' in category or 'web' in category:
                    web_tag = strong_tag.find_next_sibling('a')
                    if web_tag and web_tag.has_attr('href'):
                        web = web_tag['href']
                        
        # Organize the extracted information into a dictionary
        faculty_member = {
            'name': name,
            'title': title,
            'office': office,
            'phone': phone,
            'email': email,
            'web': web
        }

 # Insert the faculty member's information into the MongoDB collection
        professors_collection.insert_one(faculty_member)
        debug_print(f"Inserted faculty member: {name}")

    debug_print("Faculty data insertion complete.")
else:
    debug_print("Permanent Faculty page not found in the database.")

# Closes the MongoDB client connection
client.close()
debug_print("MongoDB connection closed.")
