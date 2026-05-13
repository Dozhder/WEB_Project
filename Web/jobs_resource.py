from flask_restful import Resource, abort, reqparse, inputs
from flask import jsonify, request
from functools import wraps

import datetime as dt

from data import db_session
from data.jobs import Jobs

import os
from dotenv import load_dotenv


load_dotenv('data.env')
API_KEY = os.getenv('SECRET_API_KEY')


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    session.close()
    if not job:
        abort(404, message=f"Job {job_id} not found")


def check_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key == API_KEY:
            return func(*args, **kwargs)
        else:
            abort(403, messages='Invalid API key')
    return wrapper


parsers = reqparse.RequestParser()
parsers.add_argument('team_leader', required=False, type=int)
parsers.add_argument('job', required=False)
parsers.add_argument('work_size', required=False, type=int)
parsers.add_argument('collaborators', required=False)
parsers.add_argument('hazard', required=False)
parsers.add_argument('start_date', required=False, type=inputs.datetime_from_iso8601)
parsers.add_argument('end_date', required=False, type=inputs.datetime_from_iso8601)
parsers.add_argument('is_finished', required=False, type=inputs.boolean)


class JobResource(Resource):

    @check_api_key
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.get(Jobs, job_id)
        ans = jsonify({'job': job.to_dict(
            only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'hazard', 'start_date', 'end_date',
                  'is_finished'))})
        session.close()
        return ans

    @check_api_key
    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.get(Jobs, job_id)
        session.delete(job)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    @check_api_key
    def put(self, job_id):
        abort_if_job_not_found(job_id)
        args = parsers.parse_args()
        session = db_session.create_session()
        job = session.get(Jobs, job_id)
        for key, item in args.items():
            if item is not None:
                setattr(job, key, item)
        session.commit()
        ans = jsonify({'job': job.to_dict(
            only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'hazard', 'start_date', 'end_date',
                  'is_finished'))})
        session.close()
        return ans



parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True, type=int)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('hazard', required=True)
parser.add_argument('start_date', required=False, type=inputs.datetime_from_iso8601)
parser.add_argument('end_date', required=False, type=inputs.datetime_from_iso8601)
parser.add_argument('is_finished', required=True, type=inputs.boolean)


class JobListResource(Resource):

    @check_api_key
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        ans = jsonify({'jobs': [item.to_dict(
                only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'hazard', 'start_date', 'end_date',
                      'is_finished')) for item in jobs]})
        session.close()
        return ans

    @check_api_key
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            hazard=args['hazard'],
            is_finished=args['is_finished']
        )
        if args['start_date'] is not None:
            job.start_date = args['start_date']
        if args['end_date'] is not None:
            job.end_date = args['end_date']
        session.add(job)
        session.commit()
        ans = jsonify({'id': job.id})
        session.close()
        return ans

