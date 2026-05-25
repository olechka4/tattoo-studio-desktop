import tkinter as tk
from tkinter import ttk, messagebox
from database import ClientModel, ArtistModel, AppointmentModel
from crud_windows import ClientCRUD, ArtistCRUD, AppointmentCRUD

class MainWindow:
    def __init__(self, user_data):
        self.user_id = user_data['id']
        self.username = user_data['login']
        self.full_name = user_data['full_name']
        self.email = user_data['email']
        self.phone = user_data['phone']
        self.role = user_data['role_name']
        
        self.root = tk.Tk()
        self.root.title(f"Alicia Aria Tattoo - {self.full_name}")
        self.root.geometry("1200x700")
        self.root.configure(bg="#0a0a0a")
        
        self.create_menu()
        self.create_main_content()
        
        self.root.mainloop()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="👥 Клиенты", command=self.show_clients)
        data_menu.add_command(label="🎨 Мастера", command=self.show_artists)
        data_menu.add_command(label="📅 Записи", command=self.show_appointments)
        data_menu.add_separator()
        data_menu.add_command(label="🚪 Выход", command=self.logout)
        menubar.add_cascade(label="Меню", menu=data_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_content(self):
        # Верхняя панель (как в UP.docx)
        top_frame = tk.Frame(self.root, bg="#1a1a1a", height=120)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="ALICIA ARIA", font=("Arial", 32, "bold"),
                bg="#1a1a1a", fg="#ff6b6b").pack(side=tk.LEFT, padx=40, pady=30)
        
        tk.Label(top_frame, text=f"Добро пожаловать, {self.full_name}!",
                font=("Arial", 16), bg="#1a1a1a", fg="white").pack(side=tk.RIGHT, padx=40)
        
        # Статистика
        is_admin = (self.role == 'admin')
        clients = ClientModel.get_all(self.user_id, is_admin)
        artists = ArtistModel.get_all(self.user_id, is_admin)
        appointments = AppointmentModel.get_all(self.user_id, is_admin)
        
        stats_frame = tk.Frame(self.root, bg="#0a0a0a")
        stats_frame.pack(fill=tk.X, padx=20, pady=15)
        
        stats_text = f"📊 СТАТИСТИКА СТУДИИ\n\n👥 Клиентов: {len(clients)}   |   🎨 Мастеров: {len(artists)}   |   📅 Записей: {len(appointments)}"
        tk.Label(stats_frame, text=stats_text, font=("Arial", 14),
                bg="#0a0a0a", fg="#b0b0b0", justify="center").pack(pady=15)
        
        # Последние записи
        recent_frame = tk.Frame(self.root, bg="#0a0a0a")
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(recent_frame, text="📅 ПОСЛЕДНИЕ ЗАПИСИ", font=("Arial", 16, "bold"),
                bg="#0a0a0a", fg="#ff6b6b").pack(anchor=tk.W, pady=10)
        
        columns = ("ID", "Клиент", "Мастер", "Дата", "Время", "Статус")
        tree = ttk.Treeview(recent_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180)
        
        for app in appointments[:5]:
            tree.insert("", tk.END, values=(
                app['id'], app['client_name'][:20], app['artist_name'][:20],
                app['appointment_date'], app['appointment_time'], 
                "⏳ Ожидает" if app['status'] == 'pending' else "✅ Подтверждено"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Кнопки навигации
        nav_frame = tk.Frame(self.root, bg="#0a0a0a")
        nav_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(nav_frame, text="👥 КЛИЕНТЫ", command=self.show_clients,
                 bg="#ff6b6b", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=1).pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="🎨 МАСТЕРА", command=self.show_artists,
                 bg="#ff6b6b", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=1).pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="📅 ЗАПИСИ", command=self.show_appointments,
                 bg="#ff6b6b", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=1).pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="🚪 ВЫХОД", command=self.logout,
                 bg="#444444", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=1).pack(side=tk.RIGHT, padx=10)
    
    def show_clients(self):
        ClientCRUD(self.root, self.user_id, self.role)
    
    def show_artists(self):
        ArtistCRUD(self.root, self.user_id, self.role)
    
    def show_appointments(self):
        AppointmentCRUD(self.root, self.user_id, self.role)
    
    def logout(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()
            from auth_window import AuthWindow
            AuthWindow()