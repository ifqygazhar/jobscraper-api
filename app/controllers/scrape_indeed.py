import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_indeed(keyword="programmer", location="", country="id", page=""):
    country_urls = {
        "id": "https://id.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "nl": "https://nl.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "sa": "https://sa.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "jp": "https://jp.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "cn": "https://cn.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "fr": "https://fr.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "de": "https://de.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "ar": "https://ar.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "ca": "https://ca.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "pt": "https://pt.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "co": "https://co.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "mx": "https://mx.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "my": "https://my.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "tw": "https://tw.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "in": "https://in.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "uk": "https://uk.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "ru": "https://ru.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "es": "https://es.indeed.com/jobs?q={keyword}&l={location}{page_param}",
        "it": "https://it.indeed.com/jobs?q={keyword}&l={location}{page_param}",
    }

    # Gunakan default country jika tidak valid
    if country not in country_urls:
        country = "id"

    # Tentukan parameter `start` hanya jika page tidak kosong
    page_param = f"&start={page}" if page else ""

    # Bangun URL
    url = country_urls[country].format(
        keyword=keyword, location=location, page_param=page_param
    )

    try:
        # Dapatkan instance cloudscraper
        scraper = CloudScraper.get_instance(cookies_file="app/config/indeed.json")

        # Kirim permintaan ke URL
        response = scraper.get(url)
        response.raise_for_status()
        html = response.text

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Dapatkan semua elemen pekerjaan
        job_listings = soup.find_all("li", class_="css-1ac2h1w eu4oa1w0")
        results = []

        for job in job_listings:
            # Ekstrak Judul
            title_tag = job.find("h2", class_="jobTitle")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # Ekstrak Nama Perusahaan
            company_tag = job.find("span", {"data-testid": "company-name"})
            company = company_tag.get_text(strip=True) if company_tag else "N/A"

            # Ekstrak Lokasi
            location_tag = job.find("div", {"data-testid": "text-location"})
            location = location_tag.get_text(strip=True) if location_tag else "N/A"

            # Ekstrak Deskripsi Singkat
            description_tag = job.find("ul")
            description = (
                description_tag.get_text(strip=True) if description_tag else "N/A"
            )

            # Ekstrak Link Detail Pekerjaan
            link_tag = job.find("a", class_="jcs-JobTitle")
            link = (
                f"https://{country}.indeed.com{link_tag['href']}"
                if link_tag and link_tag.has_attr("href")
                else "N/A"
            )

            # Tambahkan ke hasil hanya jika semua kolom tidak N/A
            if not (
                title == "N/A"
                and company == "N/A"
                and location == "N/A"
                and description == "N/A"
            ):
                results.append(
                    {
                        "title": title,
                        "company": company,
                        "location": location,
                        "sallary": description,
                        "link": link,
                    }
                )

        # Ekstrak Pagination
        pagination = soup.find("ul", class_="css-1g90gv6 eu4oa1w0")
        last_page = 1
        if pagination:
            page_links = pagination.find_all(
                "a", {"data-testid": re.compile(r"pagination-page-\d+")}
            )
            if page_links:
                # Ambil nomor halaman terakhir
                last_page_numbers = [
                    int(link["aria-label"])
                    for link in page_links
                    if "aria-label" in link.attrs
                ]
                if last_page_numbers:
                    last_page = max(last_page_numbers)

        # Gunakan 0 jika page kosong
        current_page = int(page)
        next_page = (
            int(page) + 10
            if page.isdigit() and int(page) + 10 < last_page * 10
            else None
        )

        return ResponseHelper.success_response(
            "Success scraping Indeed jobs",
            {
                "jobs": results,
                "pagination": {
                    "current_page": current_page,
                    "last_page": last_page,
                    "next_page": next_page,
                },
            },
        )

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
