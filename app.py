from flask import Flask

from openai import OpenAI
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os 
import logging
import ast
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()

app = Flask(__name__)
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')



def post_to_wordpress(title, content):
    url = 'https://yourwordpresssite.com/wp-json/wp/v2/posts'
    auth = HTTPBasicAuth('your_username', 'your_password')
    headers = {'Content-Type': 'application/json'}
    post = {'title': title, 'content': content, 'status': 'publish'}
    response = requests.post(url, json=post, auth=auth, headers=headers)
    return response.json()

# @app.route('/post_blog')
# def post_blog():
#     title = "My Blog Post Title"
#     content = "This is the blog post content."
#     response = post_to_wordpress(title, content)
#     return f"Post Response: {response}"


def write_post(keyword):
    system_prompt =  "You are professional copywriter. You are writing a blog post about a topic you are familiar with."
    system_prompt = system_prompt + " Output just a dictionary with keyword 'title' and 'content' and corresponding values."
    conversation =  [{"role": "system", "content": system_prompt}]
    user_prompt = f"Write a blog post about {keyword}"
    conversation.append({"role": "user", "content": user_prompt})


    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages= conversation,
        temperature=0.9,
        max_tokens=250,
        top_p=1
    )
    gpt_response = ast.literal_eval(response.choices[0].message.content)
    app.logger.debug(gpt_response)
    post_to_wordpress(gpt_response['title'], gpt_response['content'])
    

def scheduled_blog_posting():
    # Here you can define your keywords or a method to select them
    keywords = ["Keyword1", "Keyword2", "Keyword3", "Keyword4"]
    for keyword in keywords:
        write_post(keyword)

scheduler = BackgroundScheduler()
# Schedule the task to run 4 times a day
scheduler.add_job(scheduled_blog_posting, 'cron', hour='*/6')
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
    

