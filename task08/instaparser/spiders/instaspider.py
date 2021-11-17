import scrapy
from scrapy.http import HtmlResponse
import re
import json
from copy import deepcopy
from urllib.parse import urlencode
from items import InstaparserItem


class InstaspiderSpider(scrapy.Spider):
    name = 'instaspider'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_base_api_url = 'https://i.instagram.com/api/v1/friendships'
    inst_followers_path = 'followers'
    inst_following_path = 'following'
    inst_login = '<enter your instagram login>'
    inst_pwd = '<enter your instagram encrypt password>'
    users_for_parse = [
        'stellamccartney',
        'lakers'
    ]

    def parse(self, response: HtmlResponse):
        csrf = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )


    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users_for_parse:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)
        following_variables = {
            'count': 12
        }
        followers_variables = {
            'count': 12,
            'search_surface': 'follow_list_page'
        }
        following_url = f'{self.inst_base_api_url}/{user_id}/{self.inst_following_path}/?{urlencode(following_variables)}'
        followers_url = f'{self.inst_base_api_url}/{user_id}/{self.inst_followers_path}/?{urlencode(followers_variables)}'

        yield response.follow(following_url,
                              callback=self.target_user_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(following_variables),
                                         'relative_key': 'following'},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        yield response.follow(followers_url,
                              callback=self.target_user_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(followers_variables),
                                         'relative_key': 'follower'},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    
    def target_user_parse(self, response: HtmlResponse, username, user_id, variables, relative_key):
        j_data = response.json()

        if j_data.get('next_max_id'):
            variables['max_id'] = j_data.get('next_max_id')
            next_path = self.inst_followers_path if relative_key == 'follower' else self.inst_following_path
            next_url = f'{self.inst_base_api_url}/{user_id}/{next_path}/?{urlencode(variables)}'
            yield response.follow(next_url,
                              callback=self.target_user_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         'relative_key': relative_key},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        for user in j_data.get('users'):
            item = InstaparserItem(
                root_user_id=user_id,
                root_user_name=username,
                relative_key=relative_key,
                target_user_id=user.get('pk'),
                target_user_name=user.get('username'),
                target_user_avatar_url=user.get('profile_pic_url')
            )
            yield item

    def get_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')


    def get_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        user_id_str = json.loads(matched).get('id')
        return int(user_id_str)