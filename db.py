import mysql
from mysql.connector import pooling

db_config = {
    'user': 'stepan',
    'password': 'stepan',
    'host': 'mr-morkow.ru:8080',
    'database': 'farida',
}

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)


def get_connection():
    try:
        connection = pool.get_connection()
        if connection.is_connected():
            print("Успешное подключение к базе данных")
            return connection
    except mysql.connector.Error as e:
        print(f"Ошибка подключения: {e}")
        return None


def execute_query(query: str, params: tuple = ()) -> int:
    """ Выполняет запрос к базе данных и возвращает количество затронутых строк. """
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Замените на ваш хост
            user='your_username',  # Замените на ваше имя пользователя
            password='your_password',  # Замените на ваш пароль
            database='your_database'  # Замените на вашу базу данных
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows

    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if connection.is_connected():
            connection.close()



def select(query):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.commit()
            return rows
        finally:
            cursor.close()
            conn.close()  # Возвращает соединение в пул
    else:
        return None


def insert(table_name: str, data_list: list, auto_increment_id: int = 1):
    try:
        print("Start insert")

        # Получаем соединение из пула
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = [column[0] for column in cursor.fetchall()]
                columns = columns[auto_increment_id:]  # Убираем auto_increment, если нужно
                print(columns)

                placeholders = ', '.join(['%s'] * len(columns))
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                cursor.execute(query, data_list)
                row_id = cursor.lastrowid
                conn.commit()
                print("Finished insert")
                return row_id
            except Exception as e:
                print(f"Исключение при insert: {e}")
            finally:
                cursor.close()
                conn.close()  # Возвращает соединение в пул
        else:
            return None
    except Exception as e:
        print(f"Исключение при получении соединения: {e}")
        return None


def select_group_name_by_id(group_id: int):
    return select(f'''
    select name from  `groups` 
    where id = {group_id}
''')[0][0]


def delete_students(student_ids: list[int]):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Преобразуем список в строку вида (1, 2, 3)
            format_strings = ','.join(['%s'] * len(student_ids))
            query = f"DELETE FROM students WHERE id IN ({format_strings})"

            # Выполняем запрос для удаления всех студентов из списка
            cursor.execute(query, tuple(student_ids))
            conn.commit()

            rows_affected = cursor.rowcount  # Получаем количество затронутых строк
            return rows_affected
        except Exception as e:
            print(f"Error deleting students: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()  # Возвращаем соединение в пул
    else:
        return 0


def select_groups_by_teacher_id(teacher_id: int):
    return select(f'''
    select g.name, g.id from `groups` g
    join teachers t on g.teacher_id = t.teacher_id
    where t.teacher_id = "{teacher_id}"
    ''')

