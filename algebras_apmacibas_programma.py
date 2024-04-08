import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib
import random
import time

def hash_password(password):
    # parole to bytes
    password_bytes = password.encode('utf-8')
    # bytes to hash
    hashed_password = hashlib.sha256(password_bytes).hexdigest()
    return hashed_password

def register_user(conn, username, password):
    cursor = conn.cursor()
    # hashing paroli pirms ievietošanas datu bāzē
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()

def authenticate_user(conn, username, password):
    cursor = conn.cursor()
    # hashed paroles iegūšana no datu bāzes
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    if user_data:
        hashed_password = user_data[0]
        # pārbauda hashed paroli ar ievadīto
        return hashed_password == hash_password(password)
    else:
        return False

def generate_question(operation, num_range):
    if operation == "+":
        n1 = random.randint(0, num_range)
        n2 = random.randint(0, num_range)
        return f"{n1} + {n2}", n1 + n2
    elif operation == "-":
        n1 = random.randint(0, num_range)
        n2 = random.randint(0, n1)
        return f"{n1} - {n2}", n1 - n2
    elif operation == "*":
        n1 = random.randint(0, int(num_range ** 0.5))
        n2 = random.randint(0, int(num_range ** 0.5))
        return f"{n1} * {n2}", n1 * n2
    elif operation == "/":
        n2 = random.randint(1, num_range)
        result = random.randint(0, int(num_range / n2))
        n1 = result * n2
        return f"{n1} / {n2}", result

def check_answer(question, user_answer):
    try:
        if int(user_answer) == question[1]:
            return True
        else:
            return False
    except ValueError:
        return False

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS results
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      right_answers INTEGER,
                      wrong_answers INTEGER,
                      total_time INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE,
                      password TEXT)''')
    conn.commit()

def insert_result(conn, name, right_answers, wrong_answers, total_time):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO results (name, right_answers, wrong_answers, total_time)
                      VALUES (?, ?, ?, ?)''', (name, right_answers, wrong_answers, total_time))
    conn.commit()

def view_results(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()

    if not results:
        messagebox.showinfo("Rezultāti.", "Nav saglabāts neviens rezultāts.")
    else:
        result_text = "Treniņu rezultāti:\n"
        result_text += "ID | Vārds | Pareizās atbildes | Nepareizas atbildes | Izpildes laiks\n"
        for result in results:
            result_text += f"{result[0]} | {result[1]} | {result[2]} | {result[3]} | {result[4]} сек\n"
        messagebox.showinfo("Rezultāti", result_text)

def start_training(conn, username, operation, num_range):
    name = username
    right_answers = 0
    wrong_answers = 0
    start_time = time.time()

    for _ in range(5):
        question, answer = generate_question(operation, num_range)
        user_answer = tk.simpledialog.askstring("Jautājums", f"Cik būs   {question} = ")
        if user_answer is None:
            break
        if check_answer((question, answer), user_answer):
            messagebox.showinfo("Rezultāts", "Pareizi!")
            right_answers += 1
        else:
            messagebox.showinfo("Rezultāts", "Nepareizi.")
            wrong_answers += 1

    end_time = time.time()
    total_time = int(end_time - start_time)

    messagebox.showinfo("Rezultāti.", f"{name}, pareizi atrisināji {right_answers} piemērus un {wrong_answers} nepareizi.\n"
                                      f"Jūs pavadījāt piemēru risināšanai {total_time} sekundes.")

    insert_result(conn, name, right_answers, wrong_answers, total_time)
    view_results(conn)

def train(conn, username):
    training_window = tk.Toplevel()
    training_window.title("Treniņš")

    operation_label = tk.Label(training_window, text="Izvēlieties matemātisku darbību:")
    operation_label.pack()

    operation_var = tk.StringVar()
    operation_var.set("+")
    operation_option_menu = tk.OptionMenu(training_window, operation_var, "+", "-", "*", "/")
    operation_option_menu.pack()

    range_label = tk.Label(training_window, text="Izvēlieties ciparu diapazonu:")
    range_label.pack()

    range_var = tk.StringVar()
    range_var.set("1")
    range_option_menu = tk.OptionMenu(training_window, range_var, "1", "2", "3")
    range_option_menu.pack()

    start_button = tk.Button(training_window, text="Sākt apmācību", command=lambda: start_training(conn, username, operation_var.get(), int(range_var.get())))
    start_button.pack()

def main():
    conn = sqlite3.connect('results.db')
    create_table(conn)

    root = tk.Tk()
    root.title("Matemātikas prasmju apmācība")

    welcome_label = tk.Label(root, text="""Sveiki! Jūs esat ienākuši matemātisko prasmju treniņprogrammā. Iepazīsimies!
    A program for training arithmetic skills. Copyright (C) 2024 wv310""")
    welcome_label.pack()

    # lietotaja registracija
    def register_or_login():
        choice = tk.simpledialog.askstring("Darbības izvēle", "Vai jūs vēlaties reģistrēties (r) vai pierakstīties (l)?")
        if choice == "r":
            username = tk.simpledialog.askstring("Reģistrācija", "Ievadiet lietotājvārdu:")
            password = tk.simpledialog.askstring("Reģistrācija", "Ievadiet paroli:", show="*")
            # lietotaja registracija
            register_user(conn, username, password)
            messagebox.showinfo("Reģistrācija", "Jūs esat veiksmīgi reģistrējušies!")
            train(conn, username)
        elif choice == "l":
            username = tk.simpledialog.askstring("Pierakstīšanās", "Ievadiet lietotājvārdu:")
            password = tk.simpledialog.askstring("Pierakstīšanās", "Ievadiet paroli:", show="*")
            # lietotaja auntefikacija
            if authenticate_user(conn, username, password):
                messagebox.showinfo("Pierakstīšanās", "Jūs veiksmīgi pierakstījāties sistēmā!")
                train(conn, username)
            else:
                messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole.")
        else:
            messagebox.showerror("Kļūda", "Lūdzu, izvēlieties 'r', lai reģistrētos, vai 'l', lai pierakstītos.")

    register_or_login_button = tk.Button(root, text="Reģistrācija/Pierakstīšanās", command=register_or_login)
    register_or_login_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
