from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import pandas as pd
import csv, os, math

chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-gpu")  # applicable to windows os only
chrome_options.add_argument("start-maximized")  # open Browser in maximized mode
chrome_options.add_argument("disable-infobars")  # disabling infobars
chrome_options.add_argument("--disable-extensions")  # disabling extensions
chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
chrome_options.add_argument('--log-level=3')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

def identify_url(url):
  if url == base_url:
    return url
  elif url.startswith(base_url):
    parsed_url = urlparse(url)
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # Remove 'page' parameter from the query
    query_params.pop('page', None)

    # Re-encode the query string without the 'page' parameter
    new_query_string = urlencode(query_params, doseq=True)
    
    new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query_string, parsed_url.fragment))
    return new_url
  else:
    return None

def add_header():
  headers = ['Name', 'Location', 'Email', 'Phone Number']

  # Read the existing content
  with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
    existing_content = csv_file.readlines()
    # Check if the file is empty or the header does not match
    has_header = len(existing_content) > 0 and existing_content[0].strip().split(',') == headers

  # Write the header followed by the existing content if header is not found
  if not has_header:
    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow(headers)  # Writing the header
      csv_file.writelines(existing_content)

def remove_duplications():
  # Remove duplicated rows
  df = pd.read_csv(file_path)
  os.remove(file_path)
  df_unique = df.drop_duplicates()
  df_unique.to_csv(file_path, index=False, encoding='utf-8-sig')

def main():
  driver.get(input_url)
  agents_count = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'Agents_count__r8DES'))
  )
  item_num = int(agents_count.text.split(' ')[0].replace(',', ''))
  page_num = math.ceil(item_num / 24)
  for page_id in range(1, page_num + 1):
    progress_rate = int(100 * page_id / page_num)
    print(f'{progress_rate}% waiting...')
    
    page_url = identified_url + f'&page={page_id}'
    driver.get(page_url)
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="name"]'))
    )
    page_items = driver.find_element(By.CLASS_NAME, 'Agents_grid___eZGt').find_elements(By.TAG_NAME, 'a')
    for page_item in page_items:
      name = page_item.find_element(By.CSS_SELECTOR, '[data-test="name"]').text
      location = page_item.find_element(By.CSS_SELECTOR, '[data-test="location"]').text
      email = page_item.find_element(By.CSS_SELECTOR, '[data-test="email"]').text
      phone_number = page_item.find_element(By.CSS_SELECTOR, '[data-test="phone-number"]').text
      # Print and save the scraped data
      output = [name, location, email, phone_number]
      open_out = open(file_path,'a',newline="", encoding='utf-8-sig')
      file_o_csv = csv.writer(open_out, delimiter=',')
      file_o_csv.writerow(output)
      open_out.close()
  add_header()
  remove_duplications()
  print(f'The result saved as "{output_file_name}" in "{output_directory}" folder.')

if __name__ == "__main__":
  input_url = 'https://exprealty.com/agents/?page=1&country=US&location=NY'
  output_file_name = 'NY.csv'
  output_directory = 'output'
  file_path = os.path.join(output_directory, output_file_name)

  # Identify valid url
  base_url = 'https://exprealty.com/agents/'
  identified_url = identify_url(input_url)
  if identified_url == None:
    print('Please enter valid url.')
    quit()
  
  if not os.path.exists(output_directory):
    os.makedirs(output_directory)

  main()