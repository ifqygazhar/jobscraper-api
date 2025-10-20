import re
from bs4 import BeautifulSoup
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_glints(
    work="Programmer",
    job_type="FULL_TIME",
    option_work="ONSITE",
    location_id="",
    location_name="All+Cities/Provinces",
    page="1",
    cookies_file="app/config/glints.json",
):
    # Validasi parameter
    valid_job_types = ["FULL_TIME", "PART_TIME", "CONTRACT", "INTERNSHIP"]
    valid_work_options = ["ONSITE", "HYBRID", "REMOTE"]
    valid_location_name = [
        "All+Cities/Provinces",
        "Jabodetabek",
        "Banten",
        "Jawa Barat",
        "DKI Jakarta",
        "Jakarta Selatan, DKI Jakarta",
        "Jakarta Barat, DKI Jakarta",
        "Tangerang, Banten",
        "Jakarta Utara, DKI Jakarta",
        "Bandung, Jawa Barat",
    ]
    valid_location_id = [
        "",
        "JABODETABEK",
        "82f248c3-3fb3-4600-98fe-4afb47d7558d",
        "06c9e480-42e7-4f11-9d6c-67ad64ccc0f6",
        "78d63064-78a1-4577-8516-036a6c5e903e",
        "078b37b2-e791-4739-958e-c29192e5df3e",
        "af0ed74f-1b51-43cf-a14c-459996e39105",
        "ae3c458e-5947-4833-8f1b-e001ce2fad1d",
        "ea61f4ac-5864-4b2b-a2c8-aa744a2aafea",
        "86a3dc56-1bd7-4cd3-8225-d3e4b976e552",
    ]

    if job_type not in valid_job_types:
        return ResponseHelper.failure_response(
            f"Invalid job_type: {job_type}. Valid options: {valid_job_types}"
        )

    if option_work not in valid_work_options:
        return ResponseHelper.failure_response(
            f"Invalid option_work: {option_work}. Valid options: {valid_work_options}"
        )

    if location_id not in valid_location_id:
        return ResponseHelper.failure_response(
            f"Invalid location_id: {location_id}. Valid options: {valid_location_id}"
        )

    if location_name not in valid_location_name:
        return ResponseHelper.failure_response(
            f"Invalid location_name: {location_name}. Valid options: {valid_location_name}"
        )

    try:
        page = int(page)
        if page <= 0:
            return ResponseHelper.failure_response("Page must be a positive integer.")
    except ValueError:
        return ResponseHelper.failure_response(
            "Invalid page parameter. Must be an integer."
        )

    url = (
        f"https://glints.com/id/opportunities/jobs/explore?"
        f"keyword={work}+&country=ID&locationId={location_id}&locationName={location_name}&"
        f"lowestLocationLevel=1&jobTypes={job_type}&workArrangementOptions={option_work}&page={page}"
    )
    try:
        # Dapatkan instance cloudscraper dari CloudScraper Singleton
        scraper = CloudScraper.get_instance(cookies_file)

        # Kirim permintaan ke URL
        response = scraper.get(url)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Debug: Print HTML structure untuk analisis
        print("HTML Structure for debugging:")
        print(soup.prettify()[:2000])  # Print first 2000 chars

        # Coba berbagai selector untuk job cards
        job_cards = []

        # Selector 1: Original
        job_cards = soup.find_all(
            "div", {"role": "presentation", "aria-label": "Job Card"}
        )

        # Selector 2: Alternative dengan class pattern
        if not job_cards:
            job_cards = soup.find_all("div", class_=re.compile(r"JobCard"))

        print(f"Found {len(job_cards)} job cards")

        # Temukan elemen pagination dengan selector yang lebih fleksibel
        last_page = 1

        # Coba berbagai selector untuk pagination
        pagination = soup.find("div", class_=re.compile(r"Pagination"))
        if not pagination:
            pagination = soup.find("nav", {"aria-label": "pagination"})
        if not pagination:
            pagination = soup.find("div", class_=re.compile(r"pagination", re.I))

        if pagination:
            page_buttons = pagination.find_all("button")
            if page_buttons:
                # Ambil semua nomor halaman
                page_numbers = []
                for button in page_buttons:
                    text = button.get_text(strip=True)
                    if text.isdigit():
                        page_numbers.append(int(text))
                if page_numbers:
                    last_page = max(page_numbers)

        results = []
        seen_jobs = set()  # Set untuk tracking duplikat

        for job_card in job_cards:
            if not job_card:
                continue

            # Ekstrak judul pekerjaan dengan multiple selectors
            title = "N/A"
            title_tag = job_card.find("h2")
            if not title_tag:
                title_tag = job_card.find("h3")
            if not title_tag:
                title_tag = job_card.find("a", href=re.compile(r"/opportunities/jobs/"))
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Ekstrak gaji dengan pattern yang lebih fleksibel
            salary = "N/A"
            salary_tag = job_card.find("span", class_=re.compile(r"Salary", re.I))
            if not salary_tag:
                salary_tag = job_card.find(
                    "span", string=re.compile(r"Rp|IDR|\$", re.I)
                )
            if not salary_tag:
                # Cari text yang mengandung format gaji
                salary_text = job_card.get_text()
                salary_match = re.search(
                    r"Rp[\d,.\s]+|IDR[\d,.\s]+|\$[\d,.\s]+", salary_text
                )
                if salary_match:
                    salary = salary_match.group()
            if salary_tag:
                salary = salary_tag.get_text(strip=True)

            # Ekstrak lokasi
            location = "N/A"
            location_tag = job_card.find("span", class_=re.compile(r"Location", re.I))
            if not location_tag:
                location_tag = job_card.find("span", title=True)
            if location_tag:
                location = location_tag.get("title", location_tag.get_text(strip=True))

            # Ekstrak link pekerjaan
            link = "N/A"
            link_tag = job_card.find("a", href=re.compile(r"/opportunities/jobs/"))
            if link_tag:
                href = link_tag.get("href")
                if href:
                    link = f"https://glints.com{href}" if href.startswith("/") else href

            # Ekstrak nama perusahaan
            company_name = "N/A"
            company_tag = job_card.find("a", class_=re.compile(r"Company", re.I))
            if not company_tag:
                # Cari link yang mengarah ke company profile
                company_tag = job_card.find("a", href=re.compile(r"/companies/"))
            if company_tag:
                company_name = company_tag.get_text(strip=True)

            # Ekstrak logo perusahaan
            company_logo = "N/A"
            logo_tag = job_card.find("img")
            if logo_tag and logo_tag.has_attr("src"):
                company_logo = logo_tag["src"]

            # Buat unique identifier untuk mendeteksi duplikat
            # Kombinasi title, company_name, dan location sebagai key unik
            unique_key = f"{title.lower().strip()}|{company_name.lower().strip()}|{location.lower().strip()}"

            # Alternative: Gunakan link sebagai unique identifier jika ada
            if link != "N/A" and link.startswith("https://glints.com"):
                unique_key = link

            # Hanya tambahkan jika tidak duplikat dan minimal title dan company ada
            if (
                title != "N/A" or company_name != "N/A"
            ) and unique_key not in seen_jobs:
                seen_jobs.add(unique_key)
                results.append(
                    {
                        "title": title,
                        "salary": salary,
                        "location": location,
                        "company_name": company_name,
                        "company_logo": company_logo,
                        "link": link,
                    }
                )

        print(f"Successfully scraped {len(results)} unique jobs (removed duplicates)")

        # Tambahkan informasi halaman terakhir ke dalam hasil
        return ResponseHelper.success_response(
            "Success find job",
            {
                "jobs": results,
                "total_jobs": len(results),
            },
        )

    except Exception as e:
        print(f"Error in scraping: {str(e)}")
        return ResponseHelper.failure_response(f"Error: {str(e)}")
