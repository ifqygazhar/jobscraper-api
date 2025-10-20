from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.controllers.scrape_glints import scrape_glints
from app.controllers.scrape_jobstreet import scrape_jobstreet
from app.controllers.scrape_remoteok import scrape_remoteok
from app.controllers.scrape_indeed import scrape_indeed
from app.controllers.scrape_disnaker_bandung import scrape_disnaker_bandung
from app.controllers.scrape_devjobscanner import scrape_devjobscanner

# Buat router
router = APIRouter(prefix="/api", tags=["Job Scrapers"])


@router.get("/glints")
async def get_glints_jobs(
    work: str = Query(default="Programmer", description="Job title or keywords"),
    job_type: str = Query(
        default="FULL_TIME",
        description="Job type: FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP",
    ),
    option_work: str = Query(
        default="ONSITE", description="Work arrangement: ONSITE, HYBRID, REMOTE"
    ),
    location_id: str = Query(default="", description="Location ID"),
    location_name: str = Query(
        default="All+Cities/Provinces", description="Location name"
    ),
    page: str = Query(default="1", description="Page number"),
):
    """
    Scrape job listings from Glints

    - **work**: Job title or keywords to search
    - **job_type**: Type of employment (FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP)
    - **option_work**: Work arrangement (ONSITE, HYBRID, REMOTE)
    - **location_id**: ID of the location
    - **location_name**: Name of the location
    - **page**: Page number for pagination
    """
    try:
        return scrape_glints(
            work, job_type, option_work, location_id, location_name, page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobstreet")
async def get_jobstreet_jobs(
    work: str = Query(default="Programmer", description="Job title or keywords"),
    location: str = Query(default="Jakarta Raya", description="Job location"),
    country: str = Query(default="id", description="Country code"),
    page: str = Query(default="1", description="Page number"),
):
    """
    Scrape job listings from JobStreet

    - **work**: Job title or keywords to search
    - **location**: City or region
    - **country**: Country code (e.g., 'id' for Indonesia)
    - **page**: Page number for pagination
    """
    try:
        return scrape_jobstreet(work, location, country, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remoteok")
async def get_remoteok_jobs(
    keywords: str = Query(default="engineer", description="Job keywords"),
    page: int = Query(default=1, ge=1, description="Page number (minimum 1)"),
):
    """
    Scrape job listings from RemoteOK

    - **keywords**: Job keywords to search
    - **page**: Page number for pagination
    """
    try:
        return scrape_remoteok(keywords, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indeed")
async def get_indeed_jobs(
    keyword: str = Query(default="programmer", description="Job keywords"),
    location: str = Query(default="", description="Job location"),
    country: str = Query(default="id", description="Country code"),
    page: str = Query(default="0", description="Page number"),
):
    """
    Scrape job listings from Indeed

    - **keyword**: Job keywords to search
    - **location**: City or region
    - **country**: Country code (e.g., 'id' for Indonesia)
    - **page**: Page number for pagination
    """
    try:
        return scrape_indeed(keyword, location, country, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disnaker_bandung")
async def get_disnaker_bandung_jobs(
    page: str = Query(default="1", description="Page number"),
):
    """
    Scrape job listings from Disnaker Bandung

    - **page**: Page number for pagination
    """
    try:
        return scrape_disnaker_bandung(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devjobscanner")
async def get_devjobscanner_jobs(
    keywords: str = Query(default="web developer", description="Job keywords"),
    page: str = Query(default="1", description="Page number"),
):
    """
    Scrape job listings from DevJobsScanner

    - **keywords**: Job keywords to search
    - **page**: Page number for pagination
    """
    try:
        return scrape_devjobscanner(keywords, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@router.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running"""
    return {
        "status": "success",
        "message": "Job Scraper API is running",
        "version": "2.0.0",
    }
