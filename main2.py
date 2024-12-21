import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import json
import random

# initialize WebDriver using "undetected-chromedriver"
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    
    # Add a random User-Agent to avoid getting blocked
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    driver = uc.Chrome(options=options)
    return driver

# Login to Amazon
def login_to_amazon(driver, email, password):
    try:
        driver.get("https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        
        # Enter email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        
        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        # wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-link-accountList"))
        )
        print("Login successful")
    except Exception as e:
        print("Error during login:", e)
        driver.quit()

# scrape category page
def scrape_category(driver, category_url):
    data = []
    driver.get(category_url)
    time.sleep(3)
    
    # scrape product details for each page
    for _ in range(15): #for 15 pages
        products = driver.find_elements(By.XPATH, "//div[@class='zg-item-immersion']")
        
        for product in products:
            try:
                # extract basic information
                product_name = product.find_element(By.XPATH, ".//span[@class='zg-text-center-align']").text
                product_price = product.find_element(By.XPATH, ".//span[@class='p13n-sc-price']").text
                discount = product.find_element(By.XPATH, ".//span[contains(text(), '%')]").text
                rating = product.find_element(By.XPATH, ".//span[@class='a-icon-alt']").text
                best_seller_rank = product.find_element(By.XPATH, ".//span[contains(text(), '#')]").text
                ship_from = "Amazon"  # placeholder
                sold_by = "SellerName"  # placeholder
                description = "Description Not Available"  # placeholder
                number_bought = "N/A"  # placeholder
                category_name = driver.title.split(" - ")[0]
                
                # Extract image URLs
                images = product.find_elements(By.XPATH, ".//img")
                image_urls = [img.get_attribute('src') for img in images]
                
                # Filter based on discount > 50%
                if discount and int(discount.strip('%')) > 50:
                    data.append({
                        "Product Name": product_name,
                        "Product Price": product_price,
                        "Sale Discount": discount,
                        "Best Seller Rank": best_seller_rank,
                        "Rating": rating,
                        "Ship From": ship_from,
                        "Sold By": sold_by,
                        "Product Description": description,
                        "Number Bought": number_bought,
                        "Category Name": category_name,
                        "Images": image_urls
                    })
            except NoSuchElementException:
                continue
        
        # go to next page
        try:
            next_button = driver.find_element(By.XPATH, "//li[@class='a-last']/a")
            next_button.click()
            time.sleep(3)
        except NoSuchElementException:
            break
    
    return data

# Save data to CSV
def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")

# Save data to JSON
def save_to_json(data, filename):
    if not data:
        print("No data to save.")
        return
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

# Main script
if __name__ == "__main__":
    email = "example@gmail.com"  # replace with your amazon email
    password = "Amazonpass"       # replace with your amazon password
    categories = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
        "https://www.amazon.in/gp/bestsellers/books/ref=zg_bs_nav_books_0",
        "https://www.amazon.in/gp/bestsellers/health-and-personal-care/ref=zg_bs_nav_health_0",
        "https://www.amazon.in/gp/bestsellers/home-improvement/ref=zg_bs_nav_home_0",
        "https://www.amazon.in/gp/bestsellers/toys/ref=zg_bs_nav_toys_0",
        "https://www.amazon.in/gp/bestsellers/grocery/ref=zg_bs_nav_grocery_0",
        "https://www.amazon.in/gp/bestsellers/fashion/ref=zg_bs_nav_fashion_0"
    ]
    
    driver = setup_driver()
    login_to_amazon(driver, email, password)
    
    all_data = []
    for category in categories:
        print(f"Scraping category: {category}")
        category_data = scrape_category(driver, category)
        all_data.extend(category_data)
    
    driver.quit()
    
    # Save data
    save_to_csv(all_data, "amazon_best_sellers.csv")
    save_to_json(all_data, "amazon_best_sellers.json")
