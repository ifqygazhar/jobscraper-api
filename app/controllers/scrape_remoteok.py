import re
import json
from bs4 import BeautifulSoup
from flask import request
from app.helpers.response import ResponseHelper
from app.singletons.cloudscraper import CloudScraper


def scrape_remoteok(keywords="engineer", page=1):
    suggestions_keywords = [
        "engineer",
        "exec",
        "senior",
        "dev",
        "finance",
        "sys-admin",
        "javascript",
        "backend",
        "golang",
        "cloud",
        "medical",
        "front-end",
        "full-stack",
        "ops",
        "design",
        "react",
        "infosec",
        "marketing",
        "mobile",
        "content-writing",
        "saas",
        "recruiter",
        "full-time",
        "api",
        "sales",
        "ruby",
        "education",
        "devops",
        "stats",
        "python",
        "node",
        "english",
        "non-tech",
        "video",
        "travel",
        "quality-assurance",
        "ecommerce",
        "teaching",
        "linux",
        "java",
        "crypto",
        "junior",
        "git",
        "legal",
        "android",
        "accounting",
        "admin",
        "microsoft",
        "excel",
        "php",
        "amazon",
        "serverless",
        "css",
        "software",
        "analyst",
        "angular",
        "ios",
        "customer-support",
        "html",
        "salesforce",
        "ads",
        "product-designer",
        "hr",
        "sql",
        "c",
        "web-dev",
        "nosql",
        "postgres",
        "c-plus-plus",
        "part-time",
        "jira",
        "c-sharp",
        "seo",
        "apache",
        "data-science",
        "virtual-assistant",
        "react-native",
        "mongo",
        "testing",
        "architecture",
        "director",
        "music",
        "shopify",
        "wordpress",
        "laravel",
        "elasticsearch",
        "blockchain",
        "web3",
        "drupal",
        "docker",
        "graphql",
        "payroll",
        "internship",
        "machine-learning",
        "architect",
        "scala",
        "web",
        "objective-c",
        "social-media",
        "vue",
    ]

    base_url = f"https://remoteok.com/?location=Worldwide&tags={keywords}&action=get_jobs&premium=0&offset={page}0"

    try:
        # Dapatkan instance cloudscraper
        scraper = CloudScraper.get_instance()

        # Kirim permintaan ke URL
        response = scraper.get(base_url)
        response.raise_for_status()
        html = response.text

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Dapatkan semua script JSON-LD yang berisi data job
        json_ld_scripts = soup.find_all("script", type="application/ld+json")

        results = []

        for script in json_ld_scripts:
            try:
                # Parse JSON data
                job_data = json.loads(script.string)

                # Pastikan ini adalah JobPosting schema
                if job_data.get("@type") != "JobPosting":
                    continue

                # Extract data dari JSON-LD
                title = job_data.get("title", "N/A")

                # Company name dan logo dari hiringOrganization
                hiring_org = job_data.get("hiringOrganization", {})
                company_name = hiring_org.get("name", "N/A")

                # Logo bisa dari image atau hiringOrganization.logo.url
                logo_url = job_data.get("image")
                if not logo_url and hiring_org.get("logo"):
                    logo_url = hiring_org.get("logo", {}).get("url")
                if not logo_url:
                    logo_url = "N/A"

                # Extract salary
                salary_text = "N/A"
                base_salary = job_data.get("baseSalary")
                if base_salary and isinstance(base_salary, dict):
                    salary_value = base_salary.get("value", {})
                    if isinstance(salary_value, dict):
                        min_val = salary_value.get("minValue")
                        max_val = salary_value.get("maxValue")
                        currency = base_salary.get("currency", "USD")

                        if min_val and max_val:
                            # Format salary seperti di website: $60k - $120k
                            min_k = int(min_val / 1000)
                            max_k = int(max_val / 1000)
                            salary_text = f"💰 ${min_k}k - ${max_k}k"

                # Extract location
                location_text = "Worldwide"
                applicant_reqs = job_data.get("applicantLocationRequirements", [])
                if applicant_reqs and len(applicant_reqs) > 0:
                    location_name = applicant_reqs[0].get("name", "Worldwide")
                    if location_name == "Anywhere":
                        location_text = "🌏 Worldwide"
                    else:
                        location_text = f"🌏 {location_name}"

                # Find job link - cari link yang setelah script ini
                # Kita perlu mencari parent atau sibling elements
                job_link = "N/A"
                next_element = script.find_next("a")
                if next_element and next_element.get("href"):
                    href = next_element.get("href")
                    if "/remote-jobs/" in href:
                        job_link = f"https://remoteok.com{href}"

                # Tambahkan informasi ke hasil
                results.append(
                    {
                        "title": title,
                        "company_name": company_name,
                        "location": location_text,
                        "salary": salary_text,
                        "company_logo": logo_url,
                        "link": job_link,
                    }
                )

            except (json.JSONDecodeError, AttributeError, KeyError) as e:
                # Skip job yang gagal di-parse
                continue

        return ResponseHelper.success_response(
            "Success scraping RemoteOK jobs",
            {
                "jobs": results,
                "pagination": {
                    "current_page": page,
                },
            },
        )

    except Exception as e:
        return ResponseHelper.failure_response(f"Error: {str(e)}")
