"""
Python 3
Скрипт позволяет посчитать средний возраст друзей пользователя VK по его id
USAGE: ~$ python get_friends_age.py $USER_ID $VK_LOGIN $VK_PASSWD
"""
import vk_api
from sys import argv
from datetime import datetime


user_id = argv[1]
login = argv[2]
passwd = argv[3]
now = datetime.now()


def auth_handler():
    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


"""
get_user_info()
Функция получает из VK данные по ID учётной записи (УЗ):
                    * имя
                    * дата рождения (ДР)
                    * пол
Если что-то пошло не так (у пользователя скрыта ДР,
возраст подозрительно большой, нет инфы о гендере),
функция возвращает "True".
Если всё ОК, формируется и отдаётся словарь,
в котором содержится инфа на одну УЗ:
                    * id
                    * имя
                    * ДР
                    * возраст
                    * пол
"""
def get_user_info(vk, user_id):
    global now
    userInfoUnpursed = vk.users.get(user_id=user_id, fields="bdate, sex, nickname")

    try:
        bdate = userInfoUnpursed[0]['bdate']
    except KeyError:
        return True

    try:
        bdate = datetime.strptime(str(bdate), "%d.%m.%Y")
    except ValueError:
        return True

    age = int(now.year) - int(bdate.year)

    if age > 75:
        return True

    first_name = userInfoUnpursed[0]['first_name']
    last_name = userInfoUnpursed[0]['last_name']
    full_name = "{} {}".format(first_name, last_name)

    if int(userInfoUnpursed[0]['sex']) == 1:
        sex = 'W'
    elif int(userInfoUnpursed[0]['sex']) == 2:
        sex = 'M'
    else:
        return True

    userInfoPursed = {'id': user_id, 'name': full_name, 'bdate': bdate, 'sex': sex, 'age': age}

    return userInfoPursed


"""
parse_basic_info()
После того, как мы медленно и мучительно получили данные из VK,
можно начинать их обрабатывать. Эта функция делит общий список друзей
цели на два списка (men, women), подсчитывает общее количество элементов
в каждом и возвращает три словаря:
                women = {'amount': counter (Счётчик), 'items': [{'id','name','bdate','sex','age'},{},{}...] (Список словарей с данными УЗ)}
                men = {'amount': counter, 'items': men}
                people = {'amount': counter, 'items': people}
>>>print(women['items'])
[
    {
        'id': 00000000, \
        'name': 'Firstname Lastname', \
        'bdate': datetime.datetime(YEAR, M, DA, H, M), \
        'sex': 'W'/'M', \
        'age': 00
    },
    {
        'id': 1268221, \
        'name':.... etc....
    }
]
"""
def parse_basic_info(people):
    women = []
    men = []
    all_counter = 0
    w_counter = 0
    m_counter = 0

    for person in people:
        if person['sex'] == 'W':
            w_counter += 1
            women.append(person)
        else:
            m_counter += 1
            men.append(person)

        all_counter += 1

    women = {'amount': w_counter, 'items': women}
    men = {'amount': m_counter, 'items': men}
    people = {'amount': all_counter, 'items': people}

    return women, men, people


"""
parse_age_data()
Функция принимает список пользователей, рассчитвает и возвращает максимальный,
минимальный и средний возраст в спсике, количество элементов списка
"""
def parse_age_data(people):
    ages_list = []

    for person in people:
        age = int(person['age'])

        ages_list.append(age)

    ages_list.sort()
    max_age = ages_list[-1]
    min_age = ages_list[0]
    avrg_age = 0

    for element in ages_list:
        avrg_age = avrg_age + element

    avrg_age = avrg_age/len(ages_list)



    return ages_list, max_age, min_age, avrg_age, len(ages_list)


def main():
    global user_id, login, passwd
    vk_session = vk_api.VkApi(
        login, passwd,
        # функция для обработки двухфакторной аутентификации
        auth_handler=auth_handler
    )

    try:
        vk_session.auth()
        vk_session.check_sid()
        vk = vk_session.get_api()
        friends = vk.friends.get(user_id=user_id, order='hints')

        friendsParsed = []

        for friend in friends['items']:
            friendParsed = get_user_info(vk, friend)

            if friendParsed == True:
                pass
            else:
                friendsParsed.append(friendParsed)
                print(friendParsed)

        women, men, people = parse_basic_info(friendsParsed)
        w_ages_list, w_max_age, w_min_age, w_avrg_age, w_amount = parse_age_data(women['items'])
        m_ages_list, m_max_age, m_min_age, m_avrg_age, m_amount = parse_age_data(men['items'])

        string = 'Female friends\nTOTAL: {}\nMin age: {}\nMax age: {}\nAverage age: {}\n\nMale friends\nTOTAL: {}\nMin age: {}\nMax age: {}\nAverage age: {}\n\n'.format(w_amount, w_min_age, w_max_age, w_avrg_age, m_amount, m_min_age, m_max_age, m_avrg_age)
        print(string)

    except vk_api.AuthError as error_msg:
        print(error_msg)
        return


if __name__ == '__main__':
    main()
    exit()

exit()
