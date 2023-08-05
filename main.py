import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def get_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


def run_single_page(url):
    session = get_session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    page = session.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="category-book")
    job_elements = results.find_all("div", class_="col-md-12")

    for job_element in job_elements:
        address_element = job_element.find(
            "i", class_="fa-map-marker").find_next_sibling(string=True).strip()

        with open("data.txt", "a") as file:
            file.write(address_element + "\n")

    # add a delay of 300 ms to avoid getting blocked
    time.sleep(0.3)

    return soup.find("a", attrs={"aria-label": "Next"})


def get_all_categories(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="home-cat-index")
    job_elements = results.find_all("div", class_="category-item")

    all_category = []
    for job_element in job_elements:
        address_element = job_element.find("a")
        if address_element:
            href = address_element.get("href")
            if href:
                all_category.append(href)

    return all_category


def main():
    site_URL = "https://rainbowpages.lk/"
    all_category = get_all_categories(site_URL)

    page_num = 1
    for url_cat in all_category:
        print(f"Running category {url_cat}")
        URL = site_URL + url_cat
        page = get_session().get(URL)

        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(id="page-content")
        job_elements = results.find_all("div", class_="col-md-6")

        link_list = [job_element.find("a")["href"] for job_element in job_elements]

        for URL_BASE in link_list:
            try:
                next_button = run_single_page(URL_BASE)
            except Exception as e:
                print(f"Error in {URL_BASE}: {e}")
                continue

            while next_button["href"] != "#":
                next_button = next_button["href"].replace(" ", "%20")
                url = URL_BASE + next_button
                try:
                    next_button = run_single_page(url)
                except Exception as e:
                    print(f"Error in {url}: {e}")
                    break

                print(f"Page {page_num} done")
                page_num += 1

        print(f"Category {url_cat} done")

    print("All pages done")

if __name__ == "__main__":
    main()