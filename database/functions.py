import os
import uuid
import bcrypt
import pymysql


def connect():
    con = pymysql.connect(host=os.getenv("db_host"), user=os.getenv("db_user"),
                                     password=os.getenv("db_passwd"),
                                     database=os.getenv("database"), cursorclass=pymysql.cursors.DictCursor)
    return con


def find_user(email):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM account WHERE email = %s', email)
        account = cursor.fetchone()
        cursor.close()
        return account


def photo_exist(name):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM photos WHERE photo_name = %s', name)
        photo = cursor.fetchone()
        if photo is not None:
            cursor.execute('DELETE FROM photos WHERE photo_name = %s', name)
            cursor.close()
            return True
        else:
            return False


def get_photo_array():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM photos ORDER BY photo_section, load_time')
        photo_array = cursor.fetchall()
        firstRow = []
        secondRow = []
        thirdRow = []
        for iteration, photo in enumerate(photo_array):
            if int(photo['photo_section']) == 1:
                firstRow.append([iteration, photo['thumbnail']])

            if int(photo['photo_section']) == 2:
                secondRow.append([iteration, photo['thumbnail']])

            if int(photo['photo_section']) == 3:
                thirdRow.append([iteration, photo['thumbnail']])
        cursor.close()
    return firstRow, secondRow, thirdRow


def get_small_revs():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT rating, the_review, reviewer_work, rev_link, prj_id, hide FROM reviews WHERE interview_verified = "Verified"')
        rew_data = cursor.fetchall()
    cursor.close()
    return rew_data


def hide_rev(id, status):
    if find_small_review(id):
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute('UPDATE reviews SET hide = %s WHERE prj_id = %s', (status, id))
        cursor.close()
    else:
        return "ERROR"


def create_rev(rating, the_review, reviewer_work):
    connection = connect()
    with connection.cursor() as cursor:
        prj_id = str(uuid.uuid4())
        rev_link = os.getenv("CLUTCH_LINK")
        hide = False
        verified = "Verified"
        cursor.execute('INSERT INTO reviews VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s , %s)', (None, prj_id, rev_link, None, None, None, None, the_review, None, rating, None, None, None, None, None, None, reviewer_work, None, None, None, None, verified, None, hide))
    cursor.close()


def delete_rev(id):
    if find_small_review(id):
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM reviews WHERE prj_id = %s', (id))
        cursor.close()
        return None
    else:
        return "ERROR"


def find_small_review(id):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM reviews WHERE prj_id = %s', id)
        rew = cursor.fetchone()
        cursor.close()
        return rew


def update_revs_admin(id, rating, rev_work, rev):
    if find_small_review(id):
        try:
            connection = connect()
            if rating is not None:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE reviews SET rating = %s WHERE prj_id = %s', (rating, id))
                    cursor.close()
            connection = connect()
            if rev_work is not None:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE reviews SET reviewer_work = %s WHERE prj_id = %s', (rev_work, id))
                    cursor.close()
            connection = connect()
            if rev is not None:
                with connection.cursor() as cursor:
                    cursor.execute('UPDATE reviews SET the_review = %s WHERE prj_id = %s', (rev, id))
                    cursor.close()
        finally:
            return None
    else:
        return "ERROR"


def get_big_revs():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM reviews WHERE interview_verified = "Verified" and hide = false')
        rew_data = cursor.fetchall()
    cursor.close()
    return rew_data


def get_total_rate():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT rate FROM info')
        rate = cursor.fetchone()
    cursor.close()
    return rate


def get_photos_url():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT original, thumbnail, originalClass FROM photos')
        urls = cursor.fetchall()
    cursor.close()
    return urls


def create_admin(email, password):
    connection = connect()
    with connection.cursor() as cursor:
        ps_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, email))
        cursor.execute('INSERT INTO account VALUES (%s, %s, %s)', (email, ps_hash, user_uuid))
    cursor.close()


def black_list(token, email):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT %s FROM blacklist WHERE email = %s', (token, email))
        black_tokens = cursor.fetchone()
    cursor.close()


def set_blacklist(access, reftesh, email):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO blacklist VALUES (%s, %s, %s)', (access, reftesh, email))
    cursor.close()


def add_photos(load_time, photo_link_original, photo_link_thumb, photo_name, photo_section, originalClass):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO photos VALUES (%s, %s, %s, %s, %s, %s)',
                       (load_time, photo_link_original, photo_link_thumb, photo_name, photo_section, originalClass))
    cursor.close()


def create_tables():
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS account (email VARCHAR(255), password BINARY(60), uuid VARCHAR(255))')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS blacklist (access_token VARCHAR(255),refresh_token VARCHAR(255), email VARCHAR(255))')
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS photos (load_time VARCHAR(255), original VARCHAR(255), thumbnail VARCHAR(255), photo_name VARCHAR(255), photo_section VARCHAR(255), originalClass VARCHAR(255) )')
        try:
            cursor.execute('CREATE TABLE IF NOT EXISTS info (rate VARCHAR(255))')
        except:
            pass
        else:
            cursor.execute('INSERT INTO info VALUES (%s)', ("0.0"))
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS reviews (prj_name VARCHAR(255), prj_id VARCHAR(40), rev_link VARCHAR(60), prj_category VARCHAR(255), prj_size VARCHAR(60), prj_length VARCHAR(40), prj_summarry LONGTEXT, the_review LONGTEXT, review_date VARCHAR(20), rating VARCHAR(5), quality VARCHAR(5), schedule VARCHAR(5), coast VARCHAR(5), willing VARCHAR(5), feedback_summary LONGTEXT, reviewer_name VARCHAR(255), reviewer_work VARCHAR(255), interview_industry VARCHAR(255), interview_client_size VARCHAR(255), interview_location VARCHAR(255), interview_type VARCHAR(255), interview_verified VARCHAR(255), review_content_html LONGTEXT, hide BOOL)')
    cursor.close()
