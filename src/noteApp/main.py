import sys
import psycopg2
from psycopg2 import errors as pg_errors
from src.noteApp.db_connection import get_db_connection, get_cursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QMessageBox
)


class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Приложение для заметок")

        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(1200, 900)

        try:
            self.conn = get_db_connection()
            self.cursor = get_cursor(self.conn)
            QMessageBox.information(self, "Успех", "Подключено к БД.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            sys.exit(1)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        file_menu = QMenu("Файл", self)
        self.menu_bar.addMenu(file_menu)
        file_menu.addAction("Открыть").triggered.connect(self.load_notes)
        file_menu.addAction("Сохранить").triggered.connect(self.save_notes)
        file_menu.addAction("Выход").triggered.connect(self.close)

        edit_menu = QMenu("Правка", self)
        self.menu_bar.addMenu(edit_menu)
        edit_menu.addAction("Добавить заметку").triggered.connect(self.add_note)
        edit_menu.addAction("Редактировать").triggered.connect(self.edit_note)
        edit_menu.addAction("Удалить").triggered.connect(self.delete_note)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)

        # список заметок
        self.notes_list = QListWidget(self)
        main_layout.addWidget(self.notes_list)

        # подключение сигнала для выбора заметки (загрузка в форму)
        self.notes_list.itemClicked.connect(self.load_selected_note)

        # Форма для ввода/редактирования заметки
        form_layout = QVBoxLayout()

        # Поле для заголовка
        self.title_label = QLabel("Заголовок:", self)
        self.title_edit = QLineEdit(self)
        form_layout.addWidget(self.title_label)
        form_layout.addWidget(self.title_edit)

        # Поле для содержимого
        self.content_label = QLabel("Содержимое:", self)
        self.content_edit = QTextEdit(self)
        form_layout.addWidget(self.content_label)
        form_layout.addWidget(self.content_edit)

        # Горизонтальный макет для кнопок
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_note)
        buttons_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать", self)
        self.edit_button.clicked.connect(self.edit_note)
        buttons_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_note)
        buttons_layout.addWidget(self.delete_button)

        form_layout.addLayout(buttons_layout)

        main_layout.addLayout(form_layout)

        self.load_notes()

    def add_note(self):
        try:
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            self.cursor.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s)",
                (title, content)
            )
            self.conn.commit()
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка добавлена.")
        except pg_errors.UniqueViolation:
            self.conn.rollback()
            QMessageBox.warning(self, "Ошибка", "Заметка с таким заголовком уже существует.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except psycopg2.Error as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def edit_note(self):
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для редактирования.")

            old_title = selected.text()  # Старый заголовок для идентификации
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            # Обновление в БД
            self.cursor.execute(
                "UPDATE notes SET title = %s, content = %s WHERE title = %s",
                (title, content, old_title)
            )
            self.conn.commit()
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка обновлена.")
        except pg_errors.UniqueViolation:
            self.conn.rollback()
            QMessageBox.warning(self, "Ошибка", "Заметка с таким заголовком уже существует.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except psycopg2.Error as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def delete_note(self):
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для удаления.")

            title = selected.text()

            # Удаление из БД
            self.cursor.execute("DELETE FROM notes WHERE title = %s", (title,))
            self.conn.commit()
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка удалена.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except psycopg2.Error as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def load_selected_note(self, item):
        try:
            title = item.text()
            self.cursor.execute("SELECT content FROM notes WHERE title = %s", (title,))
            content = self.cursor.fetchone()[0]
            self.title_edit.setText(title)
            self.content_edit.setPlainText(content)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка загрузки: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def update_notes_list(self):
        try:
            self.notes_list.clear()
            self.cursor.execute("SELECT title FROM notes ORDER BY created_at DESC")
            titles = self.cursor.fetchall()
            for title in titles:
                self.notes_list.addItem(title[0])
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка обновления списка: {str(e)}")

    def clear_form(self):
        self.title_edit.clear()
        self.content_edit.clear()

    def load_notes(self):
        self.update_notes_list()
        QMessageBox.information(self, "Успех", "Заметки обновлены из БД.")

    def save_notes(self):
        try:
            self.conn.commit()
            QMessageBox.information(self, "Успех", "Изменения сохранены в БД.")
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка сохранения: {str(e)}")

    def closeEvent(self, event):
        self.cursor.close()
        self.conn.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())