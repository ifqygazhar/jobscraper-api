import re
from bs4 import BeautifulSoup
from flask import jsonify
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_disnaker_bandung(page="1"):
    url = f"https://disnaker.bandung.go.id/loker?page={page}"

    try:
        # Dapatkan instance cloudscraper
        scraper = CloudScraper.get_instance()

        # Kirim permintaan ke URL
        response = scraper.get(url)
        response.raise_for_status()
        html = response.text

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Dapatkan semua elemen pekerjaan
        job_elements = soup.find_all("div", class_="col-sm-3 loker")
        results = []

        for job in job_elements:
            # Ekstrak logo
            logo_tag = job.find("img")
            logo = logo_tag["src"] if logo_tag and logo_tag.has_attr("src") else "N/A"

            # Ekstrak nama perusahaan
            company_tag = job.find("p", style=re.compile(r"font-size:13px;"))
            company = company_tag.get_text(strip=True) if company_tag else "N/A"

            # Ekstrak judul pekerjaan
            title_tag = job.find("b")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            # Ekstrak lokasi
            location_tag = job.find("p", style=re.compile(r"font-size:10px;"))
            location = (
                location_tag.get_text(strip=True).replace("\n", "").replace("\r", "")
                if location_tag
                else "N/A"
            )

            # Ekstrak tanggal
            # date_tag = job.find("p", style=re.compile(r"font-size:9px;"))
            # date = (
            #     date_tag.get_text(strip=True).replace("\n", "").replace("\r", "")
            #     if date_tag
            #     else "N/A"
            # )

            # Ekstrak link detail
            link_tag = job.find("a", class_="btn btn-sm btn-danger")
            link = link_tag["href"] if link_tag and link_tag.has_attr("href") else "N/A"

            # Tambahkan hasil hanya jika semua kolom tidak kosong
            if not (
                logo == "N/A"
                and company == "N/A"
                and title == "N/A"
                and location == "N/A"
            ):
                results.append(
                    {
                        "company_logo": logo,
                        "company_name": company,
                        "title": title,
                        "location": location,
                        "salary": "Klik open untuk info gaji",
                        "link": link,
                    }
                )

        # Ekstrak total hasil dan informasi "showing"
        total_result_tag = soup.find("p", class_="small text-muted")
        total_results = 0
        showing_start = 0
        showing_end = 0

        if total_result_tag:
            match = re.search(
                r'Showing\s+<span class="fw-semibold">(\d+)</span>\s+to\s+<span class="fw-semibold">(\d+)</span>\s+of\s+<span class="fw-semibold">(\d+)</span>',
                str(total_result_tag),
            )
            if match:
                showing_start = int(match.group(1))
                showing_end = int(match.group(2))
                total_results = int(match.group(3))

        # Ekstrak pagination
        pagination_tag = soup.find("ul", class_="pagination")
        total_pages = 0
        if pagination_tag:
            page_items = pagination_tag.find_all("a", class_="page-link")
            page_numbers = [
                int(item.get_text(strip=True))
                for item in page_items
                if item.get_text(strip=True).isdigit()
            ]
            total_pages = max(page_numbers) if page_numbers else 0

        # Validasi jika halaman sudah berakhir
        if (
            showing_start == 0
            and showing_end == 0
            and total_pages == 0
            and total_results == 0
        ):
            return ResponseHelper.success_response(
                "No more data available.",
                {
                    "jobs": [],
                    "total_results": 0,
                    "showing_start": 0,
                    "showing_end": 0,
                    "total_pages": 0,
                    "current_page": int(page),
                    "is_last_page": True,
                },
            )

        return ResponseHelper.success_response(
            "Success scraping Disnaker Bandung jobs",
            {
                "jobs": results,
                "total_results": total_results,
                "showing_start": showing_start,
                "showing_end": showing_end,
                "total_pages": total_pages,
                "current_page": int(page),
                "is_last_page": showing_end == total_results,
            },
        )

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
