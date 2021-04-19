import requests
import json
import datetime
import time
from schema import *


class VkUser:

    def __init__(self):
        self.id = input('Пожалуйста, введите id пользователя: ')
        self.version = '5.126'
        with open('txts/token.txt', encoding='utf-8') as f:
            self.token = f.readline()
        self.params = {
            'access_token': self.token,
            'v': self.version,
        }
        self.url = 'https://api.vk.com/method/'
        session = Session()
        user_db = session.query(User).filter(User.user_vk_id == self.id).first()
        if not user_db:
            needed_data = ['relation', 'sex', 'bdate', 'country', 'city']
            self.data = requests.get(self.url + 'users.get',
                                     params={**self.params, **{'user_ids': self.id,
                                                               'fields': ', '.join(needed_data)
                                                               }
                                             }
                                     ).json()['response'][0]
            for position in needed_data:
                if position not in self.data:

                    if position == 'country':
                        found = False
                        start_countries = ''
                        while not found:
                            country = input(f'{start_countries}Пожалуйста, укажите вашу страну: ')
                            countries_list = requests.get(self.url + 'database.getCountries',
                                                          params={**self.params,
                                                                  **{'need_all': 1, 'count': 1000}}).json()[
                                'response']['items']
                            for current_country in countries_list:
                                if current_country['title'] == country:
                                    self.data[position] = current_country
                                    found = True
                            start_countries = 'Страна не найдена. '

                    elif position == 'city':
                        city = []
                        start_cities = ''
                        while len(city) == 0:

                            city_name = input(f'{start_cities}Пожалуйста, укажите ваш город: ')
                            print(city_name)
                            if city_name == '':
                                start_cities = 'Введена пустая строка. '
                                continue
                            city = requests.get(self.url + 'database.getCities',
                                                params={**self.params,
                                                        **{'country_id': self.data['country']['id'],
                                                           'q': city_name,
                                                           'count': 1
                                                           }
                                                        }
                                                ).json()['response']['items']
                            start_cities = 'Город не найден. '

                        self.data[position] = city[0]
                    elif position == 'bdate':
                        print(f'Пожалуйста, введите: ')

                        start_year = ''
                        correct_byear = False
                        while not correct_byear:
                            try:
                                byear = input(f'{start_year}Введите год вашего рождения: ')
                                this_year = int(datetime.datetime.today().strftime('%Y'))
                                if int(byear) and (1900 < int(byear) < (this_year - 13)):
                                    correct_byear = True
                                    self.data[position] = byear
                                else:
                                    start_year = 'Людей такого возраста нет, или ваш возраст меньше минимального (14). '
                            except ValueError:
                                start_year = 'Год введен некорректно. '

                        start_month = ''
                        correct_bmonth = False
                        while not correct_bmonth:
                            try:
                                bmonth = input(f'{start_month}Введите месяц рождения: ')
                                if int(bmonth) and (0 < int(bmonth) < 13):
                                    correct_bmonth = True
                                    self.data[position] += '.' + bmonth
                                else:
                                    start_month = 'Месяц введен некорректно. '
                            except ValueError:
                                start_month = 'Месяц введен некорректно. '

                        start_day = ''
                        correct_bday = False
                        while not correct_bday:
                            this_year = int(datetime.datetime.today().strftime('%Y'))
                            bday = input(
                                f'{start_day}Пожалуйста, введите дату (день) вашего рождения числом от 1 до 31: ')
                            try:
                                if int(bday) and (0 < int(bday) < 32):
                                    correct_bday = True
                                else:
                                    start_day = 'День введен некорректно. '
                            except ValueError:
                                start_day = 'День введен некорректно. '

                        self.data['bdate'] = '.'.join([bday, bmonth, byear])

                    elif position == 'sex':
                        correct_sex = False
                        start_sex = ''
                        while not correct_sex:
                            sex = input(f'''{start_sex}Введите ваш пол, где:
                                    1 - женский,
                                    2 - мужской
                                    ''')
                            try:
                                if int(sex) and int(sex == 1 or 2):
                                    correct_sex = True
                                    self.data['sex'] = sex
                                else:
                                    start_sex = 'Пол введен неверно. '
                            except ValueError:
                                start_sex = 'Пол введен неверно. '

                    else:
                        self.data[position] = int(input('Введите ваше семейное положение, где:\n'
                                                        '1 — не женат/не замужем,\n'
                                                        '2 — есть друг/есть подруга,\n'
                                                        '3 — помолвлен/помолвлена,\n'
                                                        '4 — женат/замужем,\n'
                                                        '5 — всё сложно,\n'
                                                        '6 — в активном поиске,\n'
                                                        '7 — влюблён/влюблена,\n'
                                                        '8 — в гражданском браке: '
                                                        )
                                                  )
            if len(self.data['bdate'].split('.')) == 2:
                correct_year = False
                start_year = ''
                while not correct_year:
                    try:
                        byear = input(f'{start_year}Введите ваш год рождения: ')
                        this_year = int(datetime.datetime.today().strftime('%Y'))
                        if int(byear) and (1900 < int(byear) < (this_year - 13)):
                            correct_year = True
                            self.data['bdate'] = self.data['bdate'] + '.' + byear

                        else:
                            start_year = 'Людей такого возраста нет, или ваш возраст меньше минимального (14). '
                    except ValueError:
                        start_year = 'Год введен некорректно. '

            add_user(self.id, self.data, 0)

        else:
            self.data = user_db.data

    def get_users(self):
        sex_set = {1, 2}
        sex_required = sex_set - {self.data["sex"]}
        byear = [int(point) for point in self.data['bdate'].split('.')][2]
        this_year = int(datetime.datetime.today().strftime('%Y'))
        age_from = this_year - byear - 2
        age_to = this_year - byear + 2
        session = Session()
        offset = session.query(User).filter(User.user_vk_id == self.id).first().offset
        resp = requests.get(self.url + 'users.search', params={**self.params, **{
            'count': 100,
            'offset': offset,
            'sort': 0,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex_required,
            'has_photo': 1,
            'city': self.data["city"]['id'],
            'status': self.data["relation"]

        }}).json()['response']['items']
        required_list = []
        i = 0

        while len(required_list) < 10:
            person = resp[i]
            used = session.query(User).filter(User.user_vk_id == self.id).first().pairs
            pairs = [pair.pair_vk_id for pair in used]

            if not person['is_closed'] and (person['id'] not in pairs):
                # print(person)
                required_list.append(person)
                add_pair(person['id'])
                add_relation(self.id, person['id'], offset)
            offset += 1
            i += 1

        return required_list

    def get_photo_and_weight(self, photo):
        this_photo = {}
        weight = photo['likes']['count'] + photo['comments']['count']
        url = photo['sizes'][-1]['url']
        this_photo['weight'], this_photo['url'] = weight, url
        return this_photo

    def get_photos(self, vk_id):
        time.sleep(0.2)
        response = requests.get(self.url + 'photos.get',
                                params={
                                    **self.params,
                                    **{
                                        'owner_id': vk_id,
                                        'album_id': 'profile',
                                        'extended': 1
                                    }
                                }
                                ).json()['response']['items']

        photos_list = []
        for photo in response:
            current_photo = self.get_photo_and_weight(photo)
            photos_list.append(current_photo)

        photos_list.sort(key=lambda x: x['weight'], reverse=True)
        photos_list = [photo['url'] for photo in photos_list]
        if len(photos_list) < 3:
            return photos_list
        else:
            return photos_list[0:3]

    def get_list_with_photos(self):
        list_of_users = self.get_users()
        list_with_photos = []
        for person in list_of_users:
            person_data = {}
            photos = user.get_photos(person['id'])
            url = 'https://vk.com/id' + str(person['id'])
            person_data['url'], person_data['photos'] = url, photos
            list_with_photos.append(person_data)
        return list_with_photos

    def json(self):
        data = self.get_list_with_photos()
        file = str(self.id) + '.json'
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)


user = VkUser()
user.json()
