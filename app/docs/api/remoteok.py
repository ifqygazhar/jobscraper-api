from flask_restx import Namespace, Resource, fields
from flask import request
from app.controllers.scrape_remoteok import scrape_remoteok

remoteok_ns = Namespace('remoteok', description='RemoteOK remote job scraping operations')

# Models untuk dokumentasi
remoteok_job_model = remoteok_ns.model('RemoteOKJob', {
    'title': fields.String(description='Job title', example='Senior Python Developer'),
    'company_name': fields.String(description='Company name', example='Remote Tech Co'),
    'location': fields.String(description='Job location', example='Worldwide'),
    'salary': fields.String(description='Job salary', example='$70k-$90k'),
    'company_logo': fields.String(description='Company logo URL'),
    'link': fields.String(description='Job link')
})

remoteok_data_model = remoteok_ns.model('RemoteOKData', {
    'jobs': fields.List(fields.Nested(remoteok_job_model)),
    'suggestions_keywords': fields.List(fields.String, description='Available keyword suggestions')
})

success_response_model = remoteok_ns.model('RemoteOKSuccessResponse', {
    'status': fields.String(description='Response status', example='success'),
    'message': fields.String(description='Response message', example='Success scraping RemoteOK jobs'),
    'data': fields.Nested(remoteok_data_model)
})

@remoteok_ns.route('')
class RemoteOKAPI(Resource):
    @remoteok_ns.doc('scrape_remoteok_jobs')
    @remoteok_ns.param('keywords', 'Job keywords to search for', default='python')
    @remoteok_ns.response(200, 'Success', success_response_model)
    def get(self):
        """Scrape remote jobs from RemoteOK"""
        keywords = request.args.get('keywords', 'python')
        
        # Langsung panggil controller asli
        return scrape_remoteok(keywords)