
from dotenv import load_dotenv
load_dotenv()
import os
import bcrypt
import redis

from flask_cors import CORS

from database.functions import create_tables, find_user, create_admin



from flask import Flask, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta
from views.admin import Reviews, ReviewsHome, GetReviews, FileUpload, GalleryHome, FileDelete, ReviewsAdmin, \
    ManageRevStatus, AddRev

app = Flask(__name__, static_folder=os.getenv("static_folder"))
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
jwt_redis_blocklist = redis.StrictRedis(host=os.getenv("redis_host"), port=os.getenv("redis_port"), db=os.getenv("redis_database"), decode_responses=os.getenv("decode_responses"))
api = Api(app, prefix=os.getenv("prefix"))
jwt = JWTManager(app)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_BLACKLIST_ENABLED'] = os.getenv("JWT_BLACKLIST_ENABLED")
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
if os.getenv("enable_cookies"):
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = os.getenv("JWT_COOKIE_CSRF_PROTECT")
app.config["JWT_COOKIE_SECURE"] = os.getenv("JWT_COOKIE_SECURE")


@app.before_first_request
def before_first_request():
    create_tables()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


class SignOut(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        jwt_redis_blocklist.set(jti, "", ex=timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))))
        return make_response(jsonify(msg="Access token revoked"), 200)


class SignIn(Resource):
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        if email and password:
            user_data = find_user(email)
            if user_data:
                hash_pwd = (user_data['password'])
                if bcrypt.checkpw(password.encode(), hash_pwd):
                    access_token = create_access_token(identity=email)
                    refresh_token = create_refresh_token(identity=email)
                    return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), 200)
                else:
                    return make_response(jsonify(msg="Bad password"), 400)
            else:
                return make_response(jsonify(msg="User not exist!"), 400)
        else:
            return make_response(jsonify(msg="Fill all Fields!"), 412)


class CreateAdmin(Resource):
    @jwt_required()
    def post(self):
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        if email and password:
            user_data = find_user(email)
            if not user_data:
                create_admin(email, password)
                return make_response(jsonify(msg="You have successfully registered!"), 201)
            else:
                return make_response(jsonify(msg="User exist!"), 400)
        else:
            return make_response(jsonify(msg="Fill all Fields!"), 412)


class Refresh(Resource):
    @jwt_required(refresh=True)
    def get(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)
        refresh_token = create_refresh_token(identity=current_user)
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), 200)


api.add_resource(SignIn, '/sign-in')
api.add_resource(Refresh, '/refresh')
api.add_resource(SignOut, '/sign-out')
api.add_resource(GetReviews, '/get-reviews')
api.add_resource(CreateAdmin, '/admin/create-admin')
api.add_resource(Reviews, '/big-reviews')
api.add_resource(ReviewsHome, '/reviews')
api.add_resource(FileUpload, '/admin/upload')
api.add_resource(GalleryHome, '/gallery')
api.add_resource(FileDelete, '/admin/delete-photo')
api.add_resource(ReviewsAdmin, '/admin/reviews')
api.add_resource(ManageRevStatus, '/admin/rev-manage')
api.add_resource(AddRev, '/admin/add-rev')
if __name__ == '__main__':
    app.run(host=os.getenv("host"), port=(os.getenv("port")), debug=(os.getenv("debug")))
