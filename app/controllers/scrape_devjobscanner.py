from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_devjobscanner(keywords="web developer", page="1"):
    # Validasi parameter page
    try:
        page = int(page)
        if page <= 0:
            return ResponseHelper.failure_response("Page must be a positive integer.")
    except (ValueError, TypeError):
        return ResponseHelper.failure_response(
            "Invalid page parameter. Must be an integer."
        )

    base_url = f"https://www.devjobsscanner.com/api/searchFull/?search={keywords}&page={page}&db=prod"

    try:
        # Dapatkan instance cloudscraper dari CloudScraper Singleton
        scraper = CloudScraper.get_instance()

        # Kirim permintaan ke URL
        response = scraper.get(base_url)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Ekstrak jobs dari response
        jobs_raw = data.get("jobs", [])

        if not jobs_raw:
            return ResponseHelper.success_response(
                "No jobs found", {"jobs": [], "total_jobs": 0, "duplicates_removed": 0}
            )

        results = []
        seen_jobs = set()  # Set untuk tracking duplikat

        for job in jobs_raw:
            if not job:
                continue

            # Ekstrak data dari job
            title = job.get("title", "N/A")
            company_name = job.get("company", "N/A")
            location = job.get("location", "N/A")

            # Format salary dari salaryMin dan salaryMax
            salary = "N/A"
            salary_min = job.get("salaryMin", -1)
            salary_max = job.get("salaryMax", -1)
            salary_currency = job.get("salaryCurrency", "")

            if salary_min > 0 and salary_max > 0:
                if salary_currency:
                    salary = f"{salary_currency} {salary_min:,.0f} - {salary_max:,.0f}"
                else:
                    salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min > 0:
                if salary_currency:
                    salary = f"{salary_currency} {salary_min:,.0f}"
                else:
                    salary = f"${salary_min:,.0f}"

            # Ekstrak company logo
            company_logo = job.get("img", "N/A")

            # Ekstrak job URL
            link = job.get("url", "N/A")

            # Buat unique identifier untuk mendeteksi duplikat
            # Gunakan job ID jika ada, atau kombinasi title + company + location
            job_id = job.get("id", "")
            if job_id:
                unique_key = job_id
            else:
                unique_key = f"{title.lower().strip()}|{company_name.lower().strip()}|{location.lower().strip()}"

            # Alternative: Gunakan link sebagai unique identifier jika ada
            if link != "N/A" and link.startswith("http"):
                unique_key = link

            # Hanya tambahkan jika tidak duplikat dan minimal title dan company ada
            if (
                title != "N/A" or company_name != "N/A"
            ) and unique_key not in seen_jobs:
                seen_jobs.add(unique_key)

                # Format sesuai dengan struktur glints
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

        print(
            f"Successfully scraped {len(results)} unique jobs from DevJobsScanner (removed duplicates)"
        )

        # Return dengan format yang sama seperti glints
        return ResponseHelper.success_response(
            "Success find job",
            {
                "jobs": results,
                "total_jobs": len(results),
            },
        )

    except ValueError as e:
        print(f"JSON parsing error: {str(e)}")
        return ResponseHelper.failure_response(f"Failed to parse response: {str(e)}")
    except Exception as e:
        print(f"Error in scraping DevJobsScanner: {str(e)}")
        return ResponseHelper.failure_response(f"Error: {str(e)}")
