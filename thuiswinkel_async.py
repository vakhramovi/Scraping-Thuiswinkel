import requests
from bs4 import BeautifulSoup as BS
import csv
import asyncio
import aiohttp

all_elements = []

async def get_page_data(session, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    with open("thuiswinkel.csv", "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=["Name", "Domain", "Location"])
        writer.writeheader()
        url = f"https://www.thuiswinkel.org/leden/?page={page}#results"
        async with session.get(url, headers=headers) as response:
            response_text = await response.text()

            soup = BS(response_text, "lxml")

            elements = soup.find("div", class_="col-span-1 lg:col-span-3").find_all("div", class_="flex flex-col relative p-4 lg:p-8 space-y-2 h-full bg-white")
            for el in elements:
                element_url = el.find("a").get("href")
                
                url = f"https://www.thuiswinkel.org/{element_url}"
                response = requests.get(url, headers=headers).text
                soup = BS(response, "lxml")

                try:
                    name = soup.find("main", id="main").find("div", class_="col-span-1").find("h1", class_="order-2").text.strip()
                except:
                    name = "None"
                try:
                    domain = soup.find("main", id="main").find_all("a", class_="text-primary-500 hover:text-primary-800 underline")[0].get("href")
                except:
                    domain = "None"
                try:
                    location = soup.find("main", id="main").find_all("div", class_="flex-1")[-2].find("div").text.strip()
                    location_lines = location.split('\n')
                    cleaned_location = '\n'.join(line.strip() for line in location_lines)
                except:
                    cleaned_location = "None"
                element_list = {
                    "Name": name,
                    "Domain": domain,
                    "Location": cleaned_location
                }
                all_elements.append(element_list)
        writer.writerows(all_elements)

async def gather_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    url = "https://www.thuiswinkel.org/leden"

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=headers)
        soup = BS(await response.text(), "lxml")
        pages_count = int(soup.find("main", id="main").find("ul", class_="flex flex-wrap space-x-2").find_all("li")[-2].find("a").text)
        tasks=[]
        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)             

def main():
    asyncio.run(gather_data())

if __name__ == "__main__":
    main()
