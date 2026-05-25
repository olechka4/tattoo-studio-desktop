import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from database import ClientModel, ArtistModel, AppointmentModel, get_clients_for_select, get_artists_for_select


class BaseCRUD:
    def __init__(self, parent, user_id, role, title, model, columns, fields):
        self.parent = parent
        self.user_id = user_id
        self.role = role
        self.model = model
        self.columns = columns
        self.fields = fields
        self.is_admin = (role == 'admin')
        
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("1000x500")
        self.window.configure(bg="#0a0a0a")
        self.window.transient(parent)
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        # Кнопки
        btn_frame = tk.Frame(self.window, bg="#0a0a0a")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="➕ ДОБАВИТЬ", command=self.add_item,
                 bg="#ff6b6b", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ РЕДАКТИРОВАТЬ", command=self.edit_item,
                 bg="#ff6b6b", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ УДАЛИТЬ", command=self.delete_item,
                 bg="#cc4444", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # ===== НОВАЯ КНОПКА ЭКСПОРТА =====
        tk.Button(btn_frame, text="📎 ЭКСПОРТ CSV", command=self.export_csv,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        # =================================
        
        # Таблица
        tree_frame = tk.Frame(self.window, bg="#0a0a0a")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Поиск
        search_frame = tk.Frame(self.window, bg="#0a0a0a")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="🔍 Поиск:", bg="#0a0a0a", fg="white").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30, bg="#2a2a2a", fg="white")
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search)
    
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = self.model.get_all(self.user_id, self.is_admin)
        self.all_data = data
        self.display_data(data)
    
    def display_data(self, data):
        for item in data:
            values = [item[col] for col in self.columns if col in item.keys()]
            self.tree.insert("", tk.END, values=values)
    
    def search(self, event):
        query = self.search_entry.get().lower()
        filtered = [item for item in self.all_data if any(query in str(item.get(col, "")).lower() for col in self.columns)]
        self.display_data(filtered)
    
    def get_selected_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись")
            return None
        values = self.tree.item(selected[0])['values']
        return values[0]
    
    # ===== НОВЫЙ МЕТОД ЭКСПОРТА В CSV =====
    def export_csv(self):
        """Экспорт данных в CSV файл"""
        if not self.all_data:
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return
        
        # Создаём папку exports, если её нет
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        # Имя файла
        filename = f"exports/{self.model.__name__}_{self.user_id}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                # Заголовки
                writer.writerow(self.columns)
                # Данные
                for item in self.all_data:
                    row = [item[col] for col in self.columns if col in item.keys()]
                    writer.writerow(row)
            
            messagebox.showinfo("Экспорт", f"✅ Данные экспортированы в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")
    # ====================================
    
    def add_item(self):
        self.open_form()
    
    def edit_item(self):
        record_id = self.get_selected_id()
        if record_id:
            self.open_form(record_id)
    
    def delete_item(self):
        record_id = self.get_selected_id()
        if record_id:
            result = messagebox.askyesno(
                "Подтверждение удаления",
                f"Вы действительно хотите удалить запись №{record_id}?\n\nЭто действие нельзя отменить, иначе хомячки останутся без обэда 🐹💔"
            )
            if result:
                success = self.model.delete(record_id)
                if success:
                    messagebox.showinfo("Успех", "✅ Запись удалена")
                    self.load_data()
                else:
                    messagebox.showerror("Ошибка", "❌ Не удалось удалить запись")
    
    def open_form(self, record_id=None):
        form = tk.Toplevel(self.window)
        form.title("Добавить запись" if not record_id else "Редактировать запись")
        form.geometry("400x450")
        form.configure(bg="#0a0a0a")
        form.transient(self.window)
        form.grab_set()
        
        entries = {}
        
        row = 0
        for field_name, field_type in self.fields:
            tk.Label(form, text=field_name, bg="#0a0a0a", fg="white",
                    font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="e")
            
            if field_type == 'combobox':
                if 'client' in field_name.lower():
                    items = get_clients_for_select()
                else:
                    items = get_artists_for_select()
                entry = ttk.Combobox(form, values=[f"{id} - {name}" for id, name in items], width=27)
            else:
                entry = tk.Entry(form, width=30, bg="#2a2a2a", fg="white", insertbackground="white")
            entry.grid(row=row, column=1, padx=10, pady=5)
            entries[field_name] = entry
            row += 1
        
        if record_id:
            data = self.model.get_all(self.user_id, self.is_admin)
            for item in data:
                if item['id'] == record_id:
                    for field_name in entries.keys():
                        if field_name in item.keys():
                            entries[field_name].insert(0, str(item[field_name]))
                    break
        
        def save():
            values = {}
            for field_name, field_type in self.fields:
                value = entries[field_name].get().strip()
                if not value:
                    messagebox.showerror("Ошибка", f"Поле '{field_name}' обязательно для заполнения")
                    return
                
                if field_type == 'int':
                    try:
                        values[field_name] = int(value)
                    except ValueError:
                        messagebox.showerror("Ошибка", f"Поле '{field_name}' должно быть числом")
                        return
                elif field_type == 'combobox':
                    if 'client' in field_name.lower():
                        values[field_name] = int(value.split(' - ')[0])
                    else:
                        values[field_name] = int(value.split(' - ')[0])
                else:
                    values[field_name] = value
            
            try:
                if record_id:
                    update_values = [values[f[0]] for f in self.fields]
                    self.model.update(record_id, *update_values)
                else:
                    create_values = [values[f[0]] for f in self.fields]
                    create_values.append(self.user_id)
                    self.model.create(*create_values)
                
                messagebox.showinfo("Успех", "✅ Сохранено!")
                form.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ {str(e)}")
        
        btn_frame = tk.Frame(form, bg="#0a0a0a")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        tk.Button(btn_frame, text="💾 СОХРАНИТЬ", command=save, bg="#4CAF50", fg="white",
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ ОТМЕНА", command=form.destroy, bg="#888888", fg="white",
                 font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)


class ClientCRUD(BaseCRUD):
    def __init__(self, parent, user_id, role):
        columns = ('id', 'name', 'phone', 'email', 'tattoo_idea')
        fields = [
            ('name', 'str'),
            ('phone', 'str'),
            ('email', 'str'),
            ('tattoo_idea', 'str'),
        ]
        super().__init__(parent, user_id, role, "👥 КЛИЕНТЫ", ClientModel, columns, fields)


class ArtistCRUD(BaseCRUD):
    def __init__(self, parent, user_id, role):
        columns = ('id', 'name', 'specialization', 'experience_years', 'bio')
        fields = [
            ('name', 'str'),
            ('specialization', 'str'),
            ('experience_years', 'int'),
            ('bio', 'str'),
        ]
        super().__init__(parent, user_id, role, "🎨 МАСТЕРА", ArtistModel, columns, fields)


class AppointmentCRUD(BaseCRUD):
    def __init__(self, parent, user_id, role):
        columns = ('id', 'client_name', 'artist_name', 'appointment_date', 'appointment_time', 'status')
        fields = [
            ('client_id', 'combobox'),
            ('artist_id', 'combobox'),
            ('appointment_date', 'str'),
            ('appointment_time', 'str'),
        ]
        super().__init__(parent, user_id, role, "📅 ЗАПИСИ", AppointmentModel, columns, fields)