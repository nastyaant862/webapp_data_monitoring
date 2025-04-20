import mysql
from pydantic import BaseModel
from mysql.connector import connect


class StandartParams(BaseModel):
    temperature: float
    time_of_process: float
    cacao: float
    chocolate_powder: float
    aromatizer: float


def connect_to_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="chocolate"
    )
    return connection


def select_all_parameters():
    connection = connect_to_db()
    cursor = connection.cursor()
    query = ''' SELECT * FROM chocolate.`текущие_параметры` '''
    cursor.execute(query)
    result = cursor.fetchall()
    for rows in result:
        print(rows)
    connection.close()


def select_standart():
    connection = connect_to_db()
    cursor = connection.cursor()

    # Запросы для получения каждого эталонного значения
    cursor.execute("SELECT значение FROM chocolate.эталонные_параметры WHERE id_эт_параметра = 1")
    temperature = cursor.fetchone()

    cursor.execute("SELECT значение FROM chocolate.эталонные_параметры WHERE id_эт_параметра = 2")
    time_of_process = cursor.fetchone()

    cursor.execute("SELECT значение FROM chocolate.эталонные_параметры WHERE id_эт_параметра = 3")
    cacao = cursor.fetchone()

    cursor.execute("SELECT значение FROM chocolate.эталонные_параметры WHERE id_эт_параметра = 4")
    chocolate_powder = cursor.fetchone()

    cursor.execute("SELECT значение FROM chocolate.эталонные_параметры WHERE id_эт_параметра = 5")
    aromatizer = cursor.fetchone()

    connection.close()

    # Проверка, что все данные были получены
    if temperature and time_of_process and cacao and chocolate_powder and aromatizer:
        return StandartParams(
            temperature=temperature[0],
            time_of_process=time_of_process[0],
            cacao=cacao[0],
            chocolate_powder=chocolate_powder[0],
            aromatizer=aromatizer[0]
        )
    return None


def select_data_for_period(period_start, period_end):
    connection = connect_to_db()
    cursor = connection.cursor()
    query = ''' SELECT эталонные_параметры.название, текущие_параметры.датавремя, 
                текущие_параметры.значение, текущие_параметры.единица_измерения 
                FROM chocolate.текущие_параметры JOIN chocolate.эталонные_параметры 
                ON текущие_параметры.id_эт_параметра = эталонные_параметры.id_эт_параметра 
                WHERE датавремя BETWEEN %s AND %s'''
    cursor.execute(query, (period_start, period_end))
    result = cursor.fetchall()
    connection.close()
    formatted_result = []
    for row in result:
        formatted_result.append(f'{row[0]} {row[1].strftime("%Y-%m-%d %H:%M:%S")} {row[2]} {row[3]}')
    # Вывод результата
    for item in formatted_result:
        print(item)
    print(formatted_result)
    return formatted_result


def insert(datetime, value, ed_izm, id_standart_value):
    connection = connect_to_db()
    cursor = connection.cursor()
    query = ''' INSERT INTO текущие_параметры (датавремя, значение, единица_измерения, id_операции, id_эт_параметра) 
                VALUES (%s, %s, %s, 1, %s) '''
    #print(query)
    cursor.execute(query, (datetime, value, ed_izm, id_standart_value))
    connection.commit()
    connection.close()


def update_standart_params(temperature, time_of_process, cacao, chocolate_powder, aromatizer):
    connection = connect_to_db()
    cursor = connection.cursor()

    # Обновляем параметры по одному запросу
    cursor.execute('''UPDATE эталонные_параметры SET значение = %s WHERE название = 'температура';''', (temperature,))
    cursor.execute('''UPDATE эталонные_параметры SET значение = %s WHERE название = 'время конширования';''', (time_of_process,))
    cursor.execute('''UPDATE эталонные_параметры SET значение = %s WHERE название = 'количество заливаемого какао-масла';''', (cacao,))
    cursor.execute('''UPDATE эталонные_параметры SET значение = %s WHERE название = 'количество шоколадного порошка';''', (chocolate_powder,))
    cursor.execute('''UPDATE эталонные_параметры SET значение = %s WHERE название = 'количество ароматизаторов';''', (aromatizer,))

    connection.commit()
    connection.close()


#
# def update_pass(id_user: str, password: str):
#     hashed_password = hash_password(password)
#
#     connection = connect_to_db()
#     cursor = connection.cursor()
#     query = '''UPDATE пользователи SET пароль = %s WHERE id_пользователя = %s'''
#     cursor.execute(query, (hashed_password, id_user))
#     connection.commit()
#     connection.close()
#     print("User's password is saved")
#
# def select_all_users():
#     connection = connect_to_db()
#     cursor = connection.cursor()
#     query = ''' SELECT * FROM chocolate.`пользователи` '''
#     cursor.execute(query)
#     result = cursor.fetchall()
#     for rows in result:
#         print(rows)
#     connection.close()
# def get_user_by_login(login: str):
#     connection = connect_to_db()
#     cursor = connection.cursor()
#     query = ''' SELECT * FROM пользователи WHERE login = %s'''
#     cursor.execute(query, (login,))
#     user = cursor.fetchone()
#     connection.close()
#     return user
