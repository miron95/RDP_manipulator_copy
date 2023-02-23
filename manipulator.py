import subprocess
import threading

import interface

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW


def get_server_user(server_ip):
    """Функция для получения данных пользователей на server_ip"""

    command = subprocess.Popen(['quser', f'/server:{server_ip}'], startupinfo=startupinfo, stdout=subprocess.PIPE,
                               encoding='IBM866',
                               stderr=subprocess.PIPE)
    try:
        result = command.communicate(timeout=5)
        output = result[0].split('\n')
    except subprocess.TimeoutExpired:
        command.kill()
        output, error = command.communicate()
    connect_list = []
    for elem in output[1:-1]:
        elem = elem.split()
        elem[-1] = elem.pop(-2) + ' ' + elem[-1]
        if elem[-3] == 'Диск':
            connect_list.append({'ID': elem[1],
                                 'Сервер': server_ip,
                                 'Пользователь': elem[0],
                                 'Сеанс': ' - ',
                                 'Статус': elem[2],
                                 'Бездействие': elem[3],
                                 'Время входа': elem[4]})

        elif elem[-3] == 'Активно':
            connect_list.append({'ID': elem[2],
                                 'Сервер': server_ip,
                                 'Пользователь': elem[0],
                                 'Сеанс': elem[1],
                                 'Статус': elem[3],
                                 'Бездействие': elem[4],
                                 'Время входа': elem[5]})

    return connect_list


def find_user(user_list: list, user_name: str) -> tuple:
    """Функция поиска данных по user_name по всем элементам user_list.  Возвращает отфильтрованный массив"""
    filter_out = tuple(item for item in user_list if item['Пользователь'].find(user_name) != -1)
    return filter_out


def connect_user(user, view: bool, server=None):
    """Функция подключение к user"""
    if type(user) == dict:
        user_id, user_server = user['ID'], user['Сервер']

    else:
        user_id = user
        user_server = server

    if view:
        command = subprocess.Popen(['mstsc', f'/v:{user_server}', '/shadow:', user_id, '/noConsentPrompt'],
                                   startupinfo=startupinfo,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        command = subprocess.Popen(['mstsc', f'/v:{user_server}', '/shadow:', user_id, '/control', '/noConsentPrompt'],
                                   startupinfo=startupinfo,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    command.communicate()


def get_servers(file: str):
    """Функция получения массива серверов из файла .txt"""

    if not file.startswith('192.'):
        with open(file, 'r', encoding='utf-8') as f:
            servers_list = tuple(line.replace('\n', '') for line in f)
    else:
        servers_list = tuple(file)
    return servers_list


def get_list_connect(username: str, first_conn: int, servers_list, view) -> tuple:
    ip_servers = get_servers(servers_list)
    users_list = []

    def ext_userslist(ip_server):
        users_list.extend(get_server_user(ip_server))

    threads = tuple(threading.Thread(target=ext_userslist, args=(ip,)) for ip in ip_servers)
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    filtered_users = find_user(users_list, user_name=username)
    if filtered_users:
        if first_conn:
            connect_user(filtered_users[0], view)
            return filtered_users

        elif not first_conn:
            return filtered_users

    else:
        interface.MainInterface.on_info_empty_username_conn()
        return filtered_users
