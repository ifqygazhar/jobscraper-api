from flask import Blueprint, request
from app.controllers.scrape_glints import scrape_glints
from app.controllers.scrape_jobstreet import scrape_jobstreet
from app.controllers.scrape_remoteok import scrape_remoteok
from app.controllers.scrape_indeed import scrape_indeed
from app.controllers.scrape_disnaker_bandung import scrape_disnaker_bandung
from app.controllers.scrape_devjobscanner import scrape_devjobscanner

scraper_bp = Blueprint("scraper", __name__)


@scraper_bp.route("/glints", methods=["GET"])
def scrape():
    try:
        # Mendapatkan parameter dari query string dengan default values
        work = request.args.get("work", "Programmer")
        job_type = request.args.get("job_type", "FULL_TIME")
        option_work = request.args.get("option_work", "ONSITE")
        page = request.args.get("page", "1")
        location_id = request.args.get("location_id", "")  # Default kosong
        location_name = request.args.get("location_name", "All+Cities/Provinces")

        # Panggil fungsi scraping dengan parameter
        return scrape_glints(
            work, job_type, option_work, location_id, location_name, page
        )
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/jobstreet", methods=["GET"])
def scrape_jobstreet_route():
    try:
        work = request.args.get("work", "Programmer")
        location = request.args.get("location", "Jakarta Raya")
        country = request.args.get("country", "id")
        page = request.args.get("page", "1")

        return scrape_jobstreet(work, location, country, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/remoteok", methods=["GET"])
def scrape_remoteok_route():
    try:
        keywords = request.args.get("keywords", "engineer")
        page = int(request.args.get("page", "1"))

        return scrape_remoteok(keywords, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/indeed", methods=["GET"])
def scrape_indeed_route():
    try:
        keyword = request.args.get("keyword", "programmer")
        location = request.args.get("location", "")
        country = request.args.get("country", "id")
        page = request.args.get("page", "0")

        return scrape_indeed(keyword, location, country, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/disnaker_bandung", methods=["GET"])
def scrape_disnaker_bandung_route():
    try:
        page = request.args.get("page", "1")
        return scrape_disnaker_bandung(page)

    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500


@scraper_bp.route("/devjobscanner", methods=["GET"])
def scrape_devjobscanner_route():
    try:
        keywords = request.args.get("keywords", "web developer")
        page = request.args.get("page", "1")

        return scrape_devjobscanner(keywords, page)
    except Exception as e:
        return {"status": "failed", "message": f"Error: {str(e)}"}, 500
