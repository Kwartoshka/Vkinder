import requests
import datetime
import time
from schema import *


class VkUser:

    def __init__(self, id):
        self.id = id
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
            add_user(self.id, self.data)
        else:
            self.data = user_db.data

    def what_i_need(self):
        needed_data = ['relation', 'sex', 'bdate', 'country', 'city']
        translations = {'relation': 'семейное положение',
                        'sex': 'пол',
                        'bdate': 'дата рождения (в формате ДД.ММ.ГГГГ)',
                        'country': 'страна',
                        'city': 'город'
                        }
        what_i_need = ['Отлично, но для дальнейшей работы мне нужны следующие данные:']
        for position in needed_data:
            if position not in self.data:
                what_i_need.append(translations[position])

        if 'bdate' in self.data and self.data['bdate'].split('.') == 2:
            what_i_need.append(translations['bdate'])
        if len(what_i_need) == 1:
            return
        what_i_need = '\n'.join(what_i_need)
        return what_i_need

    def country(self, msg):
        print(msg + 'эфывыфвыфв')
        country = msg[7:]
        print(country + 'эфывыфвыфв')
        countries_list = requests.get(self.url + 'database.getCountries',
                                      params={**self.params,
                                              **{'need_all': 1, 'count': 1000}
                                              }
                                      ).json()['response']['items']
        for current_country in countries_list:
            if current_country['title'] == country:
                self.data['country'] = current_country
                session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
                return 'Отлично, я запомнила вашу страну'
            else:
                return 'Простите, я не знаю такой страны'

    def city(self, msg):

        city_name = msg[6:]
        city = requests.get(self.url + 'database.getCities',
                            params={**self.params,
                                    **{'country_id': self.data['country']['id'],
                                       'q': city_name,
                                       'count': 1
                                       }
                                    }
                            ).json()['response']['items']
        if not city:
            return f'Простите, я не знаю такого города в вашей стране ({self.data["country"]["title"]})'
        else:
            self.data['city'] = city[0]
            session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
            return 'Отлично, я запомнила ваш город'

    def sex(self, msg):
        sex = msg[4:]
        if sex == 'женский':
            self.data['sex'] = 1
            session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
            session.commit()
            return f'Отлично, я запомнила ваш пол ({sex})'
        elif sex == 'мужской':
            self.data['sex'] = 2
            session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
            session.commit()
            return f'Отлично, я запомнила ваш пол ({sex})'
        else:
            return 'Простите, я не знаю такого пола'

    def relation(self, msg):
        relation = msg[19:]
        response = 'Хм, может с вашим семейным положением не стоит зниматься таким?\n' \
                   'Тем не менее, я запомнила ваше семейное положение'
        if relation == 'не женат' or relation == 'не замужем':
            self.data['relation'] = 1
            response = 'Отлично, я запомнила ваше семейное положение'
        elif relation == 'есть друг' or relation == 'есть подруга':
            self.data['relation'] = 2
        elif relation == 'помолвлен' or relation == 'помолвлена':
            self.data['relation'] = 3
        elif relation == 'женат' or relation == 'замужем':
            self.data['relation'] = 4
        elif relation == 'всё сложно':
            self.data['relation'] = 5
            response = 'Отлично, я запомнила ваше семейное положение'
        elif relation == 'в активном поиске':
            self.data['relation'] = 6
            response = 'Отлично, я запомнила ваше семейное положение'
        elif relation == 'влюблён' or relation == 'влюблена':
            self.data['relation'] = 7
        elif relation == 'в гражданском браке':
            self.data['relation'] = 8
        else:
            return 'Простите, такое семейное положение мне не знакомо'
        session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
        session.commit()
        return response

    def bdate(self, msg):
        bdate = msg[14:]
        if len(bdate.split('.')) == 3:
            bdate_split = [int(n) for n in bdate.split('.')]
            this_year = int(datetime.datetime.today().strftime('%Y'))
            if not isinstance(bdate_split[0], int) or not (0 < bdate_split[0] < 32):
                return 'Простите, день рождения введен некорректно'
            elif not isinstance(bdate_split[1], int) or not (0 < bdate_split[1] < 13):

                return 'Простите, месяц рождения введен некорректно'
            elif not isinstance(bdate_split[2], int) or not (1900 < bdate_split[2] < (this_year - 13)):
                return 'Простите, год введен некорректно или ваш возраст меньше минимального (14)'
            else:
                self.data['bdate'] = bdate
                session.query(User).filter(User.user_vk_id == self.id).update({"data": self.data})
                session.commit()
                return 'Отлично, я запомнила дату вашего рождения'
        else:
            return 'Простите, дата рождения введена некорректно'

    def get_users(self):
        sex_set = {1, 2}
        sex_required = sex_set - {self.data["sex"]}
        byear = [int(point) for point in self.data["bdate"].split('.')][2]
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
        this_photo['weight'], this_photo['url'], this_photo['id'], this_photo['owner_id'] = \
            weight, url, photo['id'], photo['owner_id']
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
        # photos_list = [photo['url'] for photo in photos_list]
        if len(photos_list) < 3:
            return photos_list
        else:
            return photos_list[0:3]

    def get_list_with_photos(self):
        list_of_users = self.get_users()
        list_with_photos = []
        for person in list_of_users:
            person_data = {}
            photos = self.get_photos(person['id'])
            url = 'https://vk.com/id' + str(person['id'])
            person_data['url'], person_data['photos'] = url, photos
            list_with_photos.append(person_data)
        return list_with_photos

    def get_short_list(self):
        data = self.get_list_with_photos()
        short_list = []
        for person in data:
            person_dict = {'url': person['url']}
            photos_list = []
            for photo in person['photos']:
                name = f"photo{photo['owner_id']}_{photo['id']}"
                photos_list.append(name)
            person_dict['photos'] = photos_list
            short_list.append(person_dict)
        return short_list
