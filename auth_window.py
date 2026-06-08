import tkinter as tk
from tkinter import ttk, messagebox
import re
import time
from database import init_db, UserModel

# ===== ВСЕ ВАЛИДАТОРЫ ПРЯМО ЗДЕСЬ =====

def validate_email(email):
    """Стандартная валидация email с доп. требованием: запрет admin в домене"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    # Проверка: после @ нет слова admin (любой регистр)
    domain_part = email.split('@')[1].lower()
    if 'admin' in domain_part:
        return False
    return True
    
def validate_password(password):
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    if not re.search(r'[A-Z]', password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    if not re.search(r'[0-9]', password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Пароль должен содержать хотя бы один спецсимвол"
    return True, ""

def validate_not_empty(value, field_name="Поле"):
    if not value or not value.strip():
        return False, f"{field_name} не может быть пустым"
    return True, ""


class AuthWindow:
    def __init__(self):
        init_db()
        self.root = tk.Tk()
        self.root.title("Alicia Aria Tattoo Studio - Вход")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0a")
        
        self.login_attempts = {}
        self.blocked_until = None
        
        self.create_widgets()
        self.root.mainloop()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="ALICIA ARIA", font=("Arial", 28, "bold"),
                bg="#0a0a0a", fg="#ff6b6b").pack(pady=30)
        tk.Label(main_frame, text="TATTOO STUDIO", font=("Arial", 12),
                bg="#0a0a0a", fg="#b0b0b0").pack()
        
        nb = ttk.Notebook(main_frame)
        nb.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # === Вкладка ВХОД ===
        login_frame = tk.Frame(nb, bg="#0a0a0a")
        nb.add(login_frame, text="🔐 Вход")
        
        tk.Label(login_frame, text="Логин", font=("Arial", 12),
                bg="#0a0a0a", fg="white").pack(pady=(30, 5))
        self.login_entry = tk.Entry(login_frame, width=30, font=("Arial", 11),
                                    bg="#2a2a2a", fg="white", insertbackground="white")
        self.login_entry.pack()
        
        tk.Label(login_frame, text="Пароль", font=("Arial", 12),
                bg="#0a0a0a", fg="white").pack(pady=(15, 5))
        self.password_entry = tk.Entry(login_frame, show="*", width=30, font=("Arial", 11),
                                       bg="#2a2a2a", fg="white", insertbackground="white")
        self.password_entry.pack()
        
        self.login_btn = tk.Button(login_frame, text="Войти", command=self.login,
                                   bg="#ff6b6b", fg="white", font=("Arial", 12, "bold"),
                                   width=20, height=1)
        self.login_btn.pack(pady=30)
        
        # === Вкладка РЕГИСТРАЦИЯ ===
        register_frame = tk.Frame(nb, bg="#0a0a0a")
        nb.add(register_frame, text="📝 Регистрация")
        
        fields = [
            ("Логин", "reg_login"),
            ("Пароль", "reg_password"),
            ("Подтверждение пароля", "reg_confirm"),
            ("Email", "reg_email"),
            ("Полное имя", "reg_fullname"),
            ("Телефон", "reg_phone")
        ]
        
        self.reg_entries = {}
        for label, key in fields:
            tk.Label(register_frame, text=label, font=("Arial", 10),
                    bg="#0a0a0a", fg="#b0b0b0").pack(pady=(10, 0))
            entry = tk.Entry(register_frame, width=30, 
                           show="*" if "пароль" in label.lower() else "",
                           bg="#2a2a2a", fg="white", insertbackground="white")
            entry.pack()
            self.reg_entries[key] = entry
        
        self.register_btn = tk.Button(register_frame, text="Зарегистрироваться", 
                                      command=self.register, bg="#ff6b6b", 
                                      fg="white", font=("Arial", 11, "bold"),
                                      width=25, height=1)
        self.register_btn.pack(pady=20)
    
    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get()
        
        if self.blocked_until and time.time() < self.blocked_until:
            remaining = int(self.blocked_until - time.time())
            messagebox.showerror("Блокировка", f"Слишком много попыток. Подождите {remaining} сек.")
            return
        
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        
        user = UserModel.authenticate(login, password)
        
        if user:
            self.login_attempts[login] = 0
            self.root.destroy()
            from main_window import MainWindow
            MainWindow(dict(user))
        else:
            attempts = self.login_attempts.get(login, 0) + 1
            self.login_attempts[login] = attempts
            
            if attempts >= 3:
                self.blocked_until = time.time() + 30
                messagebox.showerror("Блокировка", "3 неудачные попытки. Блокировка на 30 секунд.")
            else:
                messagebox.showerror("Ошибка", f"Неверный логин/пароль. Осталось попыток: {3 - attempts}")
    
    def register(self):
        login = self.reg_entries['reg_login'].get().strip()
        password = self.reg_entries['reg_password'].get()
        confirm = self.reg_entries['reg_confirm'].get()
        email = self.reg_entries['reg_email'].get().strip()
        full_name = self.reg_entries['reg_fullname'].get().strip()
        phone = self.reg_entries['reg_phone'].get().strip()
        
        valid, msg = validate_not_empty(login, "Логин")
        if not valid:
            messagebox.showerror("Ошибка", msg); return
        
        valid, msg = validate_password(password)
        if not valid:
            messagebox.showerror("Ошибка", msg); return
        
        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают"); return
        
        if not validate_email(email):
            messagebox.showerror("Ошибка", "Некорректный email"); return
        
        valid, msg = validate_not_empty(full_name, "Полное имя")
        if not valid:
            messagebox.showerror("Ошибка", msg); return
        
        success, result = UserModel.create(login, password, email, full_name, phone, 2)
        
        if success:
            messagebox.showinfo("Успех", "✅ Регистрация завершена! Теперь войдите.")
        else:
            messagebox.showerror("Ошибка", result)
