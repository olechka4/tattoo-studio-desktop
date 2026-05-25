import sqlite3
import hashlib

DB_NAME = "tattoo_studio.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица ролей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    ''')
    
    # Таблица клиентов (сущность 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            tattoo_idea TEXT,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Таблица мастеров (сущность 2)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            experience_years INTEGER NOT NULL,
            bio TEXT,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Таблица записей на сеанс (сущность 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            artist_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_by INTEGER NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (artist_id) REFERENCES artists (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Добавляем роли
    cursor.execute("INSERT OR IGNORE INTO roles (id, name) VALUES (1, 'admin')")
    cursor.execute("INSERT OR IGNORE INTO roles (id, name) VALUES (2, 'user')")
    
    # Админ по умолчанию (пароль: Admin123!)
    admin_password = hash_password("Admin123!")
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, login, password, email, full_name, phone, role_id)
        VALUES (1, 'admin', ?, 'admin@tattoostudio.com', 'Администратор', '+7-999-123-4567', 1)
    ''', (admin_password,))
    
    conn.commit()
    conn.close()
    
    print("✅ База данных готова!")


# Модели данных
class UserModel:
    @staticmethod
    def create(login, password, email, full_name, phone, role_id=2):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            hashed = hash_password(password)
            cursor.execute('''
                INSERT INTO users (login, password, email, full_name, phone, role_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (login, hashed, email, full_name, phone, role_id))
            conn.commit()
            return True, cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if 'login' in str(e):
                return False, "Логин уже существует"
            elif 'email' in str(e):
                return False, "Email уже зарегистрирован"
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def authenticate(login, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute('''
            SELECT u.id, u.login, u.full_name, u.email, u.phone, r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.login = ? AND u.password = ?
        ''', (login, hashed))
        user = cursor.fetchone()
        conn.close()
        return user


class ClientModel:
    @staticmethod
    def create(name, phone, email, tattoo_idea, created_by):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, phone, email, tattoo_idea, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (name.strip(), phone.strip(), email.strip() if email else None, tattoo_idea, created_by))
        conn.commit()
        client_id = cursor.lastrowid
        conn.close()
        return True, client_id
    
    @staticmethod
    def get_all(created_by=None, is_admin=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        if is_admin:
            cursor.execute("SELECT id, name, phone, email, tattoo_idea FROM clients ORDER BY name")
        else:
            cursor.execute("SELECT id, name, phone, email, tattoo_idea FROM clients WHERE created_by = ? ORDER BY name", (created_by,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def update(client_id, name, phone, email, tattoo_idea):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients SET name = ?, phone = ?, email = ?, tattoo_idea = ? WHERE id = ?
        ''', (name.strip(), phone.strip(), email.strip() if email else None, tattoo_idea, client_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(client_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        conn.close()
        return True


class ArtistModel:
    @staticmethod
    def create(name, specialization, experience_years, bio, created_by):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO artists (name, specialization, experience_years, bio, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (name.strip(), specialization.strip(), experience_years, bio, created_by))
        conn.commit()
        artist_id = cursor.lastrowid
        conn.close()
        return True, artist_id
    
    @staticmethod
    def get_all(created_by=None, is_admin=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        if is_admin:
            cursor.execute("SELECT id, name, specialization, experience_years, bio FROM artists ORDER BY name")
        else:
            cursor.execute("SELECT id, name, specialization, experience_years, bio FROM artists WHERE created_by = ? ORDER BY name", (created_by,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def update(artist_id, name, specialization, experience_years, bio):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE artists SET name = ?, specialization = ?, experience_years = ?, bio = ? WHERE id = ?
        ''', (name.strip(), specialization.strip(), experience_years, bio, artist_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(artist_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
        conn.commit()
        conn.close()
        return True


class AppointmentModel:
    @staticmethod
    def create(client_id, artist_id, date, time, created_by):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (client_id, artist_id, appointment_date, appointment_time, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (client_id, artist_id, date, time, created_by))
        conn.commit()
        app_id = cursor.lastrowid
        conn.close()
        return True, app_id
    
    @staticmethod
    def get_all(created_by=None, is_admin=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        if is_admin:
            cursor.execute('''
                SELECT a.id, c.name as client_name, art.name as artist_name, 
                       a.appointment_date, a.appointment_time, a.status
                FROM appointments a
                JOIN clients c ON a.client_id = c.id
                JOIN artists art ON a.artist_id = art.id
                ORDER BY a.appointment_date DESC
            ''')
        else:
            cursor.execute('''
                SELECT a.id, c.name as client_name, art.name as artist_name, 
                       a.appointment_date, a.appointment_time, a.status
                FROM appointments a
                JOIN clients c ON a.client_id = c.id
                JOIN artists art ON a.artist_id = art.id
                WHERE a.created_by = ?
                ORDER BY a.appointment_date DESC
            ''', (created_by,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    @staticmethod
    def update(appointment_id, client_id, artist_id, date, time):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments 
            SET client_id = ?, artist_id = ?, appointment_date = ?, appointment_time = ?
            WHERE id = ?
        ''', (client_id, artist_id, date, time, appointment_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(appointment_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        return True


def get_clients_for_select():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM clients ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [(row['id'], row['name']) for row in rows]

def get_artists_for_select():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM artists ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [(row['id'], row['name']) for row in rows]