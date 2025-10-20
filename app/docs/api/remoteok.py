from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_remoteok import scrape_remoteok

remoteok_ns = Namespace(
    "remoteok", description="RemoteOK remote job scraping operations"
)

# Models untuk dokumentasi
remoteok_job_model = remoteok_ns.model(
    "RemoteOKJob",
    {
        "title": fields.String(
            description="Job title", example="Senior Python Developer"
        ),
        "company_name": fields.String(
            description="Company name", example="Remote Tech Co"
        ),
        "location": fields.String(description="Job location", example="Worldwide"),
        "salary": fields.String(description="Job salary", example="$70k-$90k"),
        "company_logo": fields.String(description="Company logo URL"),
        "link": fields.String(description="Job link"),
    },
)

pagination_model = remoteok_ns.model(
    "Pagination",
    {
        "current_page": fields.Integer(description="Current page number", example=1),
        "next_page": fields.Integer(
            description="Next page number (null if no next page)", example=2
        ),
        "offset": fields.Integer(description="Current offset value", example=1),
    },
)

remoteok_data_model = remoteok_ns.model(
    "RemoteOKData",
    {
        "jobs": fields.List(fields.Nested(remoteok_job_model)),
        "suggestions_keywords": fields.List(
            fields.String, description="Available keyword suggestions"
        ),
        "pagination": fields.Nested(
            pagination_model, description="Pagination information"
        ),
    },
)

success_response_model = remoteok_ns.model(
    "RemoteOKSuccessResponse",
    {
        "status": fields.String(description="Response status", example="success"),
        "message": fields.String(
            description="Response message", example="Success scraping RemoteOK jobs"
        ),
        "data": fields.Nested(remoteok_data_model),
    },
)


@remoteok_ns.route("")
class RemoteOKAPI(Resource):
    @remoteok_ns.doc("scrape_remoteok_jobs")
    @remoteok_ns.param("keywords", "Job keywords to search for", default="python")
    @remoteok_ns.param(
        "page", "Page number (each page shows ~10 jobs)", type=int, default=1
    )
    @remoteok_ns.response(200, "Success", success_response_model)
    def get(self):
        """Scrape remote jobs from RemoteOK with pagination support"""
        keywords = request.args.get("keywords", "python")
        page = int(request.args.get("page", "1"))

        # Langsung panggil controller asli
        return scrape_remoteok(keywords, page)
