import psycopg2

class DatabaseManager:
    def __init__(self, database, user, password, host='localhost', port='5432'):
        self.connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )

    def create_db(self):
        with self.connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Client (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Phone (
                    id SERIAL PRIMARY KEY,
                    client_id INT NOT NULL,
                    phone_number VARCHAR(20) NOT NULL UNIQUE,
                    FOREIGN KEY (client_id) REFERENCES Client(id) ON DELETE CASCADE
                );
            """)

            self.connection.commit()
            print('Таблицы созданы успешно!')

    def add_client(self, first_name, last_name, email, phones=None):
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO Client (first_name, last_name, email)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (first_name, last_name, email))
                client_id = cur.fetchone()[0]

                if phones:
                    if not isinstance(phones, list):
                        phones = [phones]

                    for phone in phones:
                        cur.execute("""
                            INSERT INTO Phone (client_id, phone_number)
                            VALUES (%s, %s);
                        """, (client_id, phone))
                self.connection.commit()
                print(f'Клиент {first_name} {last_name} успешно добавлен с ID {client_id}.')
        except Exception as e:
            self.connection.rollback()
            print(f'Ошибка: {e}')

    def add_phone(self, client_id, phone):
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT id FROM Client WHERE id = %s;
                """, (client_id,))
                if not cur.fetchone():
                    print(f'Клиент с ID {client_id} не найден.')
                    return

                cur.execute("""
                    INSERT INTO Phone (client_id, phone_number)
                    VALUES (%s, %s);
                """, (client_id, phone))
                self.connection.commit()
                print(f'Телефон {phone} успешно добавлен клиенту с ID {client_id}.')

        except Exception as e:
            self.connection.rollback()
            print(f'Ошибка: {e}')

    def change_client(self, client_id, first_name=None, last_name=None, email=None, phones=None):
        try:
            with self.connection.cursor() as cur:
                if first_name:
                    cur.execute("""
                        UPDATE Client
                        SET first_name = %s
                        WHERE id = %s;
                    """, (first_name, client_id))

                if last_name:
                    cur.execute("""
                        UPDATE Client
                        SET last_name = %s
                        WHERE id = %s;
                    """, (last_name, client_id))

                if email:
                    cur.execute("""
                        UPDATE Client
                        SET email = %s
                        WHERE id = %s;
                    """, (email, client_id))

                if phones:
                    if not isinstance(phones, list):
                        phones = [phones]
                    self.delete_phone(client_id)
                    for phone in phones:
                        cur.execute("""
                            INSERT INTO Phone (client_id, phone_number)
                            VALUES (%s, %s);
                        """, (client_id, phone))

                self.connection.commit()
                print(f'Данные клиента с ID {client_id} успешно обновлены.')

        except Exception as e:
            self.connection.rollback()
            print(f'Ошибка: {e}')

    def delete_phone(self, client_id, phone=None):
        try:
            with self.connection.cursor() as cur:
                if phone:
                    confirmation = input(f'Удалить {phone} клиента с ID {client_id}? (да/нет): ').strip().lower()
                    if confirmation == 'да':
                        cur.execute("""
                            DELETE FROM Phone
                            WHERE client_id = %s AND phone_number = %s;
                        """, (client_id, phone))
                        self.connection.commit()
                        print(f"Телефон {phone} клиента с ID {client_id} успешно удалён.")
                    else:
                        print("Удаление отменено.")
                else:
                    confirmation = input(f'Удалить {phone} клиента с ID {client_id}? (да/нет): ').strip().lower()
                    if confirmation == 'да':
                        cur.execute("""
                            DELETE FROM Phone
                            WHERE client_id = %s;
                        """, (client_id))
                        self.connection.commit()
                        print(f'Телефоны клиента с ID {client_id} успешно удалён.')
                    else:
                        print('Удаление отменено.')

        except Exception as e:
            self.connection.rollback()
            print(f'Ошибка при удалении телефонов: {e}')

    def close(self):
        self.connection.close()
        print("Соединение с базой данных закрыто.")

if __name__ == "__main__":
    db_manager = DatabaseManager(
        database="netology_db",
        user="postgres",
        password="postgres"
    )

db_manager.create_db()
db_manager.add_client('Катя', 'Иванова', 'katyaivanova@example.com', '+123456788')
db_manager.add_client('Мила', 'Логинова', 'fhjfh@jhj.com')
db_manager.add_phone(1, '+7829282877')
db_manager.delete_phone(1, '+123456788')
db_manager.change_client(1, last_name = 'Лодочкина')
db_manager.close()