import functools
import operator
import tkinter as tk
from tkinter import ttk, messagebox

def calculate_nim_sum(piles):
    """Вычисляет Ним-сумму (XOR-сумму) для списка кучек."""
    if not piles:
        return 0
    return functools.reduce(operator.xor, piles)

def find_optimal_move(piles):
    """Находит оптимальный ход в игре Ним."""
    valid_piles = [p for p in piles if p is not None and p > 0]
    if not valid_piles:
        return None, None, True  # Игра окончена

    nim_sum = calculate_nim_sum(valid_piles)

    if nim_sum == 0:
        for i, pile_size in enumerate(piles):
            if pile_size is not None and pile_size > 0:
                return i, 1, False  # Любой ход (проигрышная позиция)
        return None, None, True

    for i, pile_size in enumerate(piles):
        if pile_size is None or pile_size <= 0:
            continue

        target_size = pile_size ^ nim_sum
        if target_size < pile_size:
            amount_to_take = pile_size - target_size
            return i, amount_to_take, False

    return None, None, False

def get_pile_name(index):
    """Преобразует индекс кучки (0-3) в имя (A-D)."""
    return chr(ord('A') + index)

def int_to_binary(n, width=5):
    """Преобразует число в двоичную строку с фиксированной шириной."""
    return bin(n)[2:].zfill(width)

class NimApp:
    def __init__(self, master):
        self.master = master
        master.title("Подсказчик для игры Ним")
        master.geometry("750x550")
        master.minsize(550, 450)

        # Настройка веса строк и столбцов
        master.grid_rowconfigure(4, weight=1)
        for i in range(4):
            master.grid_columnconfigure(i, weight=1)

        # Шрифты
        self.title_font = ("Arial", 12, "bold")
        self.result_font = ("Courier New", 12)
        self.bold_font = ("Courier New", 12, "bold")
        self.details_font = ("Arial", 9)
        self.button_font = ("Arial", 10)

        # Заголовок
        tk.Label(master, text="Введите количество яблок в кучках:", font=self.title_font).grid(
            row=0, column=0, columnspan=4, pady=10, sticky="nsew"
        )

        # Поля ввода с кнопками +/-
        self.pile_entries = []
        self.current_piles = [tk.StringVar(master, value='0') for _ in range(4)]

        for i in range(4):
            frame = ttk.Frame(master)
            frame.grid(row=2, column=i, padx=5, pady=5, sticky="nsew")

            # Кнопка "-1"
            btn_minus = ttk.Button(
                frame, text="-", width=2,
                command=lambda idx=i: self.adjust_pile(idx, -1)
            )
            btn_minus.pack(side=tk.LEFT, fill=tk.Y)

            # Поле ввода
            entry = ttk.Entry(
                frame, width=5, textvariable=self.current_piles[i],
                font=self.result_font, justify=tk.CENTER
            )
            entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            entry.bind("<FocusIn>", self.handle_focus_in)
            entry.bind("<KeyRelease>", self.validate_entry)
            self.pile_entries.append(entry)

            # Кнопка "+1"
            btn_plus = ttk.Button(
                frame, text="+", width=2,
                command=lambda idx=i: self.adjust_pile(idx, +1)
            )
            btn_plus.pack(side=tk.LEFT, fill=tk.Y)

            # Метка кучки
            label = tk.Label(master, text=f"Кучка {get_pile_name(i)}:", font=self.result_font)
            label.grid(row=1, column=i, padx=5, pady=5, sticky="ew")

        # Кнопка расчета
        self.calculate_button = ttk.Button(
            master, text="Рассчитать ход", command=self.calculate_move, style="TButton"
        )
        self.calculate_button.grid(row=3, column=0, columnspan=4, pady=15, sticky="nsew")

        # Поле результата
        self.result_frame = ttk.Frame(master)
        self.result_frame.grid(row=4, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

        self.result_text = tk.Text(
            self.result_frame, wrap=tk.WORD, font=self.result_font, height=10, padx=5, pady=5
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.result_frame, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

        # Кнопка "Показать детали"
        self.details_button = ttk.Button(
            master, text="Показать детали расчета", command=self.toggle_details
        )
        self.details_button.grid(row=5, column=0, columnspan=4, pady=5, sticky="ew")
        self.details_shown = False

    def handle_focus_in(self, event):
        """Выделяет текст при клике в поле, если там '0'."""
        entry = event.widget
        if entry.get() == "0":
            entry.select_range(0, tk.END)

    def validate_entry(self, event):
        """Заменяет пустое поле на '0' и проверяет ввод."""
        entry = event.widget
        text = entry.get()
        
        if not text:
            entry.insert(0, "0")
        elif not text.isdigit():
            # Удаляем нечисловые символы
            entry.delete(0, tk.END)
            entry.insert(0, "".join(filter(str.isdigit, text)))

    def adjust_pile(self, pile_idx, delta):
        """Изменяет значение кучки на +/-1 с проверкой на минимум 0."""
        current_val = int(self.current_piles[pile_idx].get())
        new_val = max(0, current_val + delta)
        self.current_piles[pile_idx].set(str(new_val))

    def toggle_details(self):
        """Показывает/скрывает детали расчета."""
        self.details_shown = not self.details_shown
        self.details_button.config(
            text="Скрыть детали" if self.details_shown else "Показать детали"
        )
        self.calculate_move()

    def calculate_move(self):
        piles = []
        try:
            for i in range(4):
                val = self.current_piles[i].get()
                piles.append(int(val) if val else 0)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа!")
            return

        current_nim_sum = calculate_nim_sum([p for p in piles if p > 0])
        pile_index, amount_to_take, game_over = find_optimal_move(piles)

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        if game_over:
            self.result_text.insert(tk.END, "🎮 Игра окончена. Все кучки пусты.\n")
        elif pile_index is None:
            self.result_text.insert(tk.END, "❌ Ошибка: не удалось определить ход.\n")
        elif current_nim_sum == 0:
            pile_name = get_pile_name(pile_index)
            self.result_text.insert(tk.END, "⚠️ Вы в проигрышной позиции (Ним-сумма = 0).\n\n", "bold")
            self.result_text.insert(tk.END, f"Любой ход (например, взять 1 из {pile_name}) ", "bold")
            self.result_text.insert(tk.END, "даст оппоненту преимущество.\n", "bold")
        else:
            pile_name = get_pile_name(pile_index)
            self.result_text.insert(tk.END, "✅ ", "bold")
            self.result_text.insert(tk.END, "Оптимальный ход:\n", "bold")
            self.result_text.insert(tk.END, f"➡ Возьмите {amount_to_take} из кучки {pile_name}\n\n", "bold")
            
            new_piles = list(piles)
            new_piles[pile_index] -= amount_to_take
            new_state = ", ".join([f"{get_pile_name(i)}={new_piles[i]}" for i in range(4)])
            self.result_text.insert(tk.END, f"Новое состояние: {new_state}\n")

        if self.details_shown:
            self.add_detailed_calculation(piles, current_nim_sum, pile_index, amount_to_take)

        self.result_text.tag_config("bold", font=self.bold_font)
        self.result_text.tag_config("details_title", font=("Arial", 10, "bold"))
        self.result_text.tag_config("details_subtitle", font=("Arial", 9, "bold"))
        self.result_text.tag_config("details", font=("Courier New", 9))
        self.result_text.config(state=tk.DISABLED)

    def add_detailed_calculation(self, piles, nim_sum, move_idx, move_amount):
        """Добавляет детали расчета в результат."""
        self.result_text.insert(tk.END, "\n--- Детали расчета ---\n", "details_title")
        
        # Двоичные представления
        self.result_text.insert(tk.END, "Двоичные представления:\n", "details_subtitle")
        for i, pile in enumerate(piles):
            bin_str = int_to_binary(pile)
            self.result_text.insert(tk.END, f"{get_pile_name(i)}: {pile} = {bin_str}\n", "details")
        
        # Ним-сумма
        self.result_text.insert(tk.END, "\nНим-сумма (XOR всех кучек):\n", "details_subtitle")
        bin_nim_sum = int_to_binary(nim_sum)
        self.result_text.insert(tk.END, f"Результат: {nim_sum} = {bin_nim_sum}\n", "details")
        
        # Стратегия
        self.result_text.insert(tk.END, "\nСтратегия:\n", "details_subtitle")
        if nim_sum == 0:
            self.result_text.insert(tk.END, "• Ним-сумма = 0 → это проигрышная позиция.\n", "details")
            self.result_text.insert(tk.END, "• Если оппонент не ошибётся, вы проиграете.\n", "details")
        else:
            self.result_text.insert(tk.END, "• Ним-сумма ≠ 0 → можно выиграть.\n", "details")
            self.result_text.insert(tk.END, f"• Берём {move_amount} из {get_pile_name(move_idx)}, чтобы обнулить сумму.\n", "details")
            self.result_text.insert(tk.END, "• После этого оппонент окажется в проигрышной позиции.\n", "details")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10, "bold"))
    app = NimApp(root)
    root.mainloop()