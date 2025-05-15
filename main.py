import sqlite3
import psutil
import datetime

DB_NAME = 'system_monitor.db'


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS system_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL
        );
        ''')


def perform_monitoring():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cpu = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory().percent

    disk = psutil.disk_usage('/').percent

    with get_db() as db:
        db.execute('''
            INSERT INTO system_stats (timestamp, cpu_usage, memory_usage, disk_usage)
            VALUES (?, ?, ?, ?)
        ''', (now, cpu, mem, disk))

    print(f"Данные сохранены: {now}")
    print(f"CPU: {cpu}%, RAM: {mem}%, Disk: {disk}%")


def view_data():
    with get_db() as db:
        records = db.execute('SELECT * FROM system_stats ORDER BY timestamp DESC').fetchall()
        if not records:
            print("Нет сохраненных данных.")
            return
        print(f"{'ID':<5} {'Время':<20} {'CPU%':<6} {'RAM%':<6} {'Disk%':<6}")
        for rec in records:
            print(
                f"{rec['id']:<5} {rec['timestamp']:<20} {rec['cpu_usage']:<6.2f} {rec['memory_usage']:<6.2f} {rec['disk_usage']:<6.2f}")


def main_menu():
    init_db()

    while True:
        print("\n--- Системный монитор ---")
        print("1. Провести мониторинг и сохранить данные")
        print("2. Посмотреть сохраненные данные")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            perform_monitoring()
        elif choice == '2':
            view_data()
        elif choice == '0':
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == '__main__':
    main_menu()