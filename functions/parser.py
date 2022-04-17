import os

from bs4 import BeautifulSoup
import asyncio
import aiohttp

from database.functions import connect


core_url = os.getenv("CLUTCH_LINK")
rev_URL = core_url + "#reviews"


def find_review(id):
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM reviews WHERE prj_id = %s', id)
        rew = cursor.fetchone()
        cursor.close()
        return rew


async def get_site_content():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(rev_URL) as resp:
                text = await resp.read()
        except Exception as e:
            print(e)

    return BeautifulSoup(text.decode('utf-8'), 'html5lib')

loop = asyncio.get_event_loop()
site_data = loop.run_until_complete(get_site_content())
loop.close()


def get_reviews(html):
    try:
        reviews_html = html.find_all('div', class_='review_data--container')
        tolal_rate_html = html.find('div', class_='field-name-total-reviews')
        tolal_rate = tolal_rate_html.find('span', class_='rating').text.strip()
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute('UPDATE info SET rate =  (%s)', (tolal_rate))
            cursor.close()
        for i in reviews_html:
            prj_name = i.find('a', class_='inner_url').text.strip()
            prj_name_html = i.find('a', class_='inner_url')
            prj_id = prj_name_html['href']
            rev_link = core_url + prj_id
            prj_category = i.find('div', class_='field field-name-project-type field-inline custom_popover').text.strip()
            prj_size = i.find('div', class_='field field-name-cost field-inline custom_popover').text.strip()
            prj_length = i.find('div', class_='field field-name-project-length field-inline custom_popover').text.strip()
            prj_summarry_html = i.find('div', class_='field field-name-proj-description field-inline')
            prj_summarry = prj_summarry_html.find('div', class_='field-item').text.strip()
            the_review = i.find('div', class_='field field-name-client-quote field-inline').text.strip()
            review_date = i.find('h5', class_='h5_title date').text.strip()
            rating = i.find('span', class_='rating').text.strip()

            quality_html = i.find('div', class_='field field-name-quality field-inline')
            quality = quality_html.find('div', class_='field-item').text.strip()

            schedule_html = i.find('div', class_='field field-name-schedule field-inline')
            schedule = schedule_html.find('div', class_='field-item').text.strip()

            cost_html = i.find('div', class_='field field-name-cost-feedback field-inline')
            cost = cost_html.find('div', class_='field-item').text.strip()

            willing_to_refer_html = i.find('div', class_='field field-name-willingness-refer field-inline')
            willing_to_refer = willing_to_refer_html.find('div', class_='field-item').text.strip()

            feedback_summary_html = i.find('div', class_='field field-name-comments field-inline')
            feedback_summary = feedback_summary_html.find('div', class_='field-item').text.strip()
            reviewer_html = i.find('div', class_='group-reviewer')

            reviewer_work = reviewer_html.find('div', class_='field-item').text.strip()
            if reviewer_html.find('div', class_='field-name-full-name-display') is not None:
                reviewer_name = reviewer_html.find('div', class_='field-name-full-name-display').text.strip()
            else:
                reviewer_name = "The Reviewer"

            interview_html = i.find('div', class_='group-interview')
            interview_industry = interview_html.find('div', class_='field-name-user-industry field-inline custom_popover').text.strip()
            interview_client_size = interview_html.find('div', class_='field-name-company-size field-inline custom_popover').text.strip()
            interview_location = interview_html.find('div', class_='field-name-location field-inline custom_popover').text.strip()
            interview_type_html = interview_html.find('div', class_='field-name-review-type text-tip field-inline custom_popover')
            interview_type = interview_type_html.find('div', class_='field-item').text.strip()
            interview_verified = interview_html.find('div', class_='field-name-verified field-inline custom_popover').text.strip()

            VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br']


            review_content_html = i.find('div', class_='review-content').text.strip()
            # for tag in review_content_html.findAll(True):
            #     if tag.name not in VALID_TAGS:
            #         tag.hidden = True
            # review_content_html.renderContents()
            if not find_review(prj_id):
                connection = connect()
                with connection.cursor() as cursor:
                    hide = False
                    cursor.execute('INSERT INTO reviews VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s , %s)', (prj_name, prj_id, rev_link, prj_category, prj_size, prj_length, prj_summarry, the_review, review_date, rating, quality, schedule, cost, willing_to_refer, feedback_summary, reviewer_name, reviewer_work, interview_industry, interview_client_size, interview_location, interview_type, interview_verified, review_content_html, hide))
                    cursor.close()
            # print(f'================================================')
            # print(f'========{prj_name}========')
            # print(f'Review id: {prj_id}')
            # print(f'Review link: {rev_link}')
            # print(f'Category: {prj_category} ')
            # print(f'Size: {prj_size} ')
            # print(f'Length: {prj_length} ')
            # print(f'Summarry: {prj_summarry} ')
            # print(f'Review: {the_review} ')
            # print(f'Review date: {review_date} ')
            # print(f'Rate: {rating} ')
            # print(f'Rate info: {quality}--{schedule}--{cost}--{willing_to_refer}')
            # print(f'Feedback summary: {feedback_summary}')
            # print(f'{reviewer_name} works: {reviewer_work}')
            # print(f'{interview_industry}, {interview_client_size}, {interview_location}, {interview_type}, {interview_verified}')
            # print(f'=================================================')
            # print(f'====================REVIEW=======================')
            # print(f'{review_content_html}')
            # print(f'=================================================')
    except Exception as e:
        print(e)


def rev_store():
    try:
        get_reviews(site_data)
    except Exception as e:
        print(e)
