from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import re
import os

# Step 1: Save outer HTML using Selenium
def save_page_html():
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    # service = Service('C:\\Drivers\\chromedriver.exe')  # Update with your actual ChromeDriver path
    driver = webdriver.Chrome(options=chrome_options)

    # URL of the Facebook post
    post_url = "https://www.facebook.com/salmanmd.sultan.1/posts/pfbid02pwk1KyH6jtefw3dYQuPQPEESmxCrBGaigyWUdu5JRSbZzAQBAnRDfZsPP7av5ikql"

    # Load the page
    driver.get(post_url)

    # Wait for manual login if needed
    print("Please log in to Facebook manually in the browser if required (disable headless mode if needed).")
    time.sleep(10)  # Adjust time for manual login

    # Scroll and click "View more comments" to load all comments
    while True:
        try:
            more_comments = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='View more comments']"))
            )
            more_comments.click()
            time.sleep(2)  # Wait for comments to load
        except:
            break  # No more comments to load

    # Save the outer HTML
    html_content = driver.page_source
    with open('facebook_post.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Saved page HTML to facebook_post.html")

    # Clean up
    driver.quit()

# Step 2: Parse HTML file with BeautifulSoup
def parse_comments_from_html():
    # Check if HTML file exists
    if not os.path.exists('facebook_post.html'):
        print("Error: facebook_post.html not found. Run save_page_html() first.")
        return

    # Read the saved HTML file
    with open('facebook_post.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find comment containers
    comments_data = []
    comment_blocks = soup.find_all('div', {'data-ad-comet-preview': 'comment'})

    for block in comment_blocks:
        try:
            # Extract commenter's name
            name_tag = block.find('span', class_=re.compile('xt0psk2'))
            name = name_tag.get_text(strip=True) if name_tag else "Unknown"

            # Extract profile link
            profile_tag = name_tag.find_parent('a', href=True) if name_tag else None
            profile_link = profile_tag['href'] if profile_tag else "N/A"
            if profile_link != "N/A":
                profile_link = f"https://www.facebook.com{profile_link}" if not profile_link.startswith('http') else profile_link

            # Extract comment text
            comment_tag = block.find('div', {'data-ad-preview': 'message'})
            comment = comment_tag.get_text(strip=True) if comment_tag else "No comment text"

            comments_data.append({
                "commenter_name": name,
                "profile_link": profile_link,
                "comment": comment
            })
        except Exception as e:
            print(f"Error parsing comment block: {e}")
            continue

    # Save data to JSON file
    with open('facebook_comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments_data, f, ensure_ascii=False, indent=4)

    print(f"Collected {len(comments_data)} comments. Saved to facebook_comments.json")

# Execute both steps
if __name__ == "__main__":
    save_page_html()
    parse_comments_from_html()