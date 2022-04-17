import os

from flask import make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask import request, jsonify
from database.functions import get_small_revs, get_total_rate, get_big_revs, add_photos, get_photos_url, photo_exist, \
    get_photo_array, update_revs_admin, hide_rev, delete_rev, create_rev
from functions.parser import rev_store
from werkzeug.utils import secure_filename
from PIL import Image
from time import time
import uuid

LINK = os.getenv("STATIC_LINK")
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
MAX_FILES_UPLOAD = int(os.getenv("MAX_FILES_UPLOAD"))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def split(arr):
    arrs = []
    while len(arr) > 2:
        pice = arr[:2]
        arrs.append(pice)
        arr = arr[2:]
    arrs.append(arr)
    return arrs


class FileUpload(Resource):
    #@jwt_required()
    def post(self):
        section = request.form['section']
        if 'file' not in request.files:
            return make_response(jsonify(msg="No file part in the request", type="Error"), 400)
        files = request.files.getlist('file')
        if len(files) <= MAX_FILES_UPLOAD:
            errors = {}
            success = False
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_name = str(uuid.uuid4()) + filename
                    file.save(os.path.join('static/original', unique_name))
                    img = Image.open(file)
                    img.thumbnail((640, 428), Image.ANTIALIAS)
                    img.save(os.path.join('static/thumb', unique_name))
                    link = LINK + 'original/' + unique_name
                    link_thumb = LINK + 'thumb/' + unique_name
                    add_photos(time(), link, link_thumb, unique_name, section, 'gallary-photo')
                    success = True
                else:
                    errors[file.filename] = 'File type is not allowed'
            if success:
                return make_response(jsonify(msg="Files successfully uploaded", type="Success"), 201)
            else:
                return make_response(jsonify(msg="Server error", type="Error", errors=errors), 500)
        else:
            return make_response(jsonify(msg="File count exceeded!", type="Error"), 500)


class FileDelete(Resource):
    #@jwt_required()
    def delete(self):
        filename = request.json.get("filename", None)
        if filename:
            if photo_exist(filename):
                os.remove('static/original/' + filename)
                os.remove('static/thumb/' + filename)
                return make_response(jsonify(msg="Photo removed!", type="Success"), 204)
            else:
                return make_response(jsonify(msg="Not exist", type="Error"), 400)
        return make_response(jsonify(msg="No filename!", type="Error"), 400)


class GetReviews(Resource):
    #@jwt_required()
    def get(self):
        rev_store()
        return make_response(jsonify(msg="New data uploaded", type="Success"), 201)


class GalleryHome(Resource):
    def get(self):
        images = get_photos_url()
        firstRow, secondRow, thirdRow = get_photo_array()
        return make_response(jsonify(images=images, firstRow=firstRow, secondRow=secondRow, thirdRow=thirdRow), 200)


class Reviews(Resource):
    def get(self):
        data = get_big_revs()
        return make_response(jsonify(data), 200)


class ReviewsHome(Resource):
    def get(self):
        reviewsArray = get_small_revs()
        reviewsArrayMobile = split(reviewsArray)
        rate = get_total_rate()['rate']
        return make_response(jsonify(reviewsArray=reviewsArray, reviewsArrayMobile=reviewsArrayMobile, rate=rate), 200)


class ReviewsAdmin(Resource):
    #@jwt_required()
    def post(self):
        id = request.json.get("prj_id", None)
        rate = request.json.get("rating", None)
        work = request.json.get("reviewer_work", None)
        rev = request.json.get("the_review", None)
        if not id:
            return make_response(jsonify(msg="No id", type="Error"), 400)
        else:
            if not rate and not work and not rev:
                return make_response(jsonify(msg="no data!", type="Error"), 400)
            else:
                errors = update_revs_admin(id, rate, work, rev)
                if errors is not None:
                    return make_response(jsonify(msg="Review not found", type="Error"), 400)
                else:
                    return make_response(jsonify(msg="Edited", type="Success"), 200)


class ManageRevStatus(Resource):
    #@jwt_required()
    def post(self):
        id = request.json.get("prj_id", None)
        status = request.json.get("hide", None)
        if not id and not status:
            return make_response(jsonify(msg="No valid data!", type="Error"), 400)
        else:
            errors = hide_rev(id, status)
            if errors:
                return make_response(jsonify(msg="Review not found", type="Error"), 400)
            else:
                return make_response(jsonify(msg="Changed!", type="Success"), 200)

    #@jwt_required()
    def delete(self):
        id = request.json.get("prj_id", None)
        if not id:
            return make_response(jsonify(msg="No valid data!", type="Error"), 400)
        else:
            errors = delete_rev(id)
            if errors:
                return make_response(jsonify(msg="Review not found", type="Error"), 400)
            else:
                return make_response(jsonify(msg="Deleted!", type="Success"), 200)


class AddRev(Resource):
    #@jwt_required()
    def post(self):
        rating = request.json.get("rating", None)
        reviewer_work = request.json.get("reviewer_work", None)
        the_review = request.json.get("the_review", None)
        if not rating and not reviewer_work and not the_review:
            return make_response(jsonify(msg="No valid data!", type="error"), 400)
        else:
            create_rev(rating, the_review, reviewer_work)
            return make_response(jsonify(msg="Created!", type="Success"), 200)

