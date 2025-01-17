import tkinter as tk
from tkinter import messagebox
import json
import os

# Класс SudokuBoard - игровое поле
class SudokuBoard:
    # Инициализация пустого игрового поля
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    # Метод для загрузки игрового поля из файла
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.board = json.load(file)
        except FileNotFoundError:
            raise Exception(f"Файл {filename} не найден.")
        except json.JSONDecodeError:
            raise Exception(f"Некорректный формат файла {filename}.")

    # Метод для сохранения игрового поля в файл
    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.board, file)

# Класс MainMenu - меню игры
class MainMenu:
    # Инициализация меню
    def __init__(self, master):
        self.master = master
        self.master.title("Sudoku")
        self.master.geometry("450x550")
        self.master.resizable(False, False)
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        # Отображение заголовка и кнопок выбора уровня
        title = tk.Label(self.frame, text="Судоку для всех", font=('Arial', 20))
        title.pack(pady=20)
        level_choose = tk.Label(self.frame, text="Выберите уровень", font=('Arial', 15))
        level_choose.pack(pady=20)

        self.levels = self.get_levels()
        for level in self.levels:
            button = tk.Button(self.frame, text=f"Уровень {level}", command=lambda l=level: self.start_game(l))
            button.pack(pady=5)

    # Получение списка доступных уровней из директории
    def get_levels(self):
        levels_dir = "levels"
        return sorted([name for name in os.listdir(levels_dir) if os.path.isdir(os.path.join(levels_dir, name)) and name.isdigit()], key=int)

    # Запуск игры для выбранного уровня
    def start_game(self, level):
        self.frame.destroy()
        SudokuGame(self.master, level)

# Класс SudokuGame - игровой процесс
class SudokuGame:
    def __init__(self, master, level):
        self.master = master
        self.master.title(f"Sudoku. Уровень {level}")
        self.level_dir = f"levels/{level}"
        self.frame = tk.Frame(self.master)
        self.frame.pack()

        # Создание атрибутов игры
        self.board_model = SudokuBoard()
        self.cells = []
        self.initial_cells = set()
        self.solution = None
        self.lives = 3

        # Инициализация интерфейса и загрузка данных
        self.create_widgets()
        self.load_initial_board()
        self.load_solution()

    # Создание виджетов интерфейса
    def create_widgets(self):
        self.canvas = tk.Canvas(self.frame, width=450, height=450)
        self.canvas.pack()

        # Создание ячеек игрового поля
        cell_size = 50
        for row in range(9):
            row_cells = []
            for col in range(9):
                x = col * cell_size
                y = row * cell_size

                cell = tk.Entry(self.frame, font=('Arial', 18), justify='center', width=2)
                cell.place(x=x + 5, y=y + 5, width=cell_size - 10, height=cell_size - 10)
                cell.bind("<KeyRelease>", lambda event, r=row, c=col: self.validate_input(event, r, c))  # Проверка ввода
                row_cells.append(cell)
            self.cells.append(row_cells)

        # Отображение линий, разделяющих блоки
        self.canvas.create_line(0, 3 * cell_size, 450, 3 * cell_size, width=3)
        self.canvas.create_line(3 * cell_size, 0, 3 * cell_size, 450, width=3)
        self.canvas.create_line(0, 6 * cell_size, 450, 6 * cell_size, width=3)
        self.canvas.create_line(6 * cell_size, 0, 6 * cell_size, 450, width=3)

        # Кнопка для сохранения состояния игры
        tk.Button(self.frame, text="Сохранить игру", command=self.save_game).pack(side=tk.LEFT, padx=10, pady=10)

        # Проверка наличия сохраненной игры
        saving_file = os.path.join(self.level_dir, "saving.json")
        if os.path.exists(saving_file):
            try:
                with open(saving_file, 'r') as file:
                    data = json.load(file)
                if data:
                    # Если есть сохраненная игра, отображение кнопки для загрузки состояния игры
                    tk.Button(self.frame, text="Загрузить игру", command=self.load_saved_game).pack(side=tk.LEFT, padx=10, pady=10)
            except (json.JSONDecodeError, FileNotFoundError):
                self.back_to_menu()
                raise Exception(f"Файл не найден. ")

        # Кнопка для возвращения в меню
        tk.Button(self.frame, text="Назад", command=self.back_to_menu).pack(side=tk.RIGHT, padx=10, pady=10)

        # Отображение количества оставшихся жизней
        lives_text = "Жизни: " + " ".join(["☻"] * self.lives)
        self.lives_label = tk.Label(self.frame, text=lives_text, font=('Arial', 15), fg="red")
        self.lives_label.pack(side=tk.BOTTOM, pady=10)

    # Обновление отображения количества жизней
    def update_lives_display(self):
        lives_text = "Жизни: " + " ".join(["☻"] * self.lives)
        self.lives_label.config(text=lives_text)

    # Загрузка решения из файла
    def load_solution(self):
        try:
            with open(os.path.join(self.level_dir, "solution.json"), 'r') as file:
                self.solution = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл с решением solution.json не найден.")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Некорректный формат файла solution.json.")

    # Проверка верности введенной пользователем цифры
    def validate_input(self, event, row, col):
        value = self.cells[row][col].get()
        if value.isdigit():
            num = int(value)
            if 1 <= num <= 9:
                if self.solution and self.solution[row][col] == num:
                    self.board_model.board[row][col] = num
                    self.cells[row][col].config(bg="green")
                    self.check_victory()
                else:
                    self.cells[row][col].config(bg="red")
                    self.lives -= 1
                    self.update_lives_display()
                    if self.lives == 0:
                        self.game_over()
            else:
                self.cells[row][col].config(bg="red")
                self.lives -= 1
                self.update_lives_display()
                if self.lives == 0:
                    self.game_over()
        elif value == "":
            self.board_model.board[row][col] = 0
            self.cells[row][col].config(bg="white")
        else:
            self.cells[row][col].config(bg="red")
            self.lives -= 1
            self.update_lives_display()
            if self.lives == 0:
                self.game_over()

    # Проверка, достигнута ли победа
    def check_victory(self):
        for row in range(9):
            for col in range(9):
                if self.board_model.board[row][col] != self.solution[row][col]:
                    return
        self.victory()

    # Очистка файла сохранения
    def clear_saving_file(self):
        saving_file = os.path.join(self.level_dir, "saving.json")
        try:
            with open(saving_file, 'w') as file:
                file.write('{}')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось очистить файл сохранения: {str(e)}")

    # Демонстрация доп окна в случае победы
    def victory(self):
        self.clear_saving_file()
        result = messagebox.showinfo("Игра окончена", "Вы победили!")
        if result:
            self.back_to_menu()

    # Демонстрация доп окна в случае проигрыша
    def game_over(self):
        self.clear_saving_file()
        result = messagebox.showinfo("Игра окончена", "Вы проиграли(")
        if result:
            self.back_to_menu()

    # Обновление отображения игрового поля
    def update_display(self):
        for row in range(9):
            for col in range(9):
                value = self.board_model.board[row][col]
                cell = self.cells[row][col]
                cell.delete(0, tk.END)
                if value != 0:
                    cell.insert(0, str(value))
                    if (row, col) in self.initial_cells:
                        cell.config(state="disabled", disabledforeground="black", bg="gray")
                    else:
                        if self.solution and self.solution[row][col] == value:
                            cell.config(bg="green")
                        else:
                            cell.config(bg="red")
                else:
                    cell.config(bg="white")

    # Сохранение состояния игры
    def save_game(self):
        try:
            self.board_model.save_to_file(os.path.join(self.level_dir, "saving.json"))
            messagebox.showinfo("Сохранение", "Игра сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка при сохранении", str(e))

    # Загрузка сохраненного состояния игры
    def load_saved_game(self):
        try:
            self.board_model.load_from_file(os.path.join(self.level_dir, "saving.json"))
            self.update_display()
            messagebox.showinfo("Загрузка", "Игра загружена!")
        except Exception as e:
            messagebox.showerror("Ошибка при загрузке сохраненного состояния", str(e))

    # Загрузка начального состояния поля
    def load_initial_board(self):
        try:
            self.board_model.load_from_file(os.path.join(self.level_dir, "level.json"))
            for row in range(9):
                for col in range(9):
                    if self.board_model.board[row][col] != 0:
                        self.initial_cells.add((row, col))
            self.update_display()
        except Exception as e:
            messagebox.showerror("Ошибка при загрузке начального состояния", str(e))

    # Возврат в главное меню
    def back_to_menu(self):
        self.frame.destroy()
        MainMenu(self.master)

root = tk.Tk()
MainMenu(root)
root.mainloop()
