import sys
import hashlib
import psycopg2
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QListWidget, QMessageBox, QTabWidget, QDialog,
    QFormLayout, QDialogButtonBox
)
from db_connection import get_db_connection, get_cursor
from PyQt6.QtGui import QIcon
from psycopg2 import errors as pg_errors
import uuid


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход")
        layout = QFormLayout(self)

        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Логин:", self.username_edit)
        layout.addRow("Пароль:", self.password_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация")
        layout = QFormLayout(self)

        self.username_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Логин:", self.username_edit)
        layout.addRow("Пароль:", self.password_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Приложение для заметок")
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
        self.setMaximumSize(1200, 900)
        self.setWindowIcon(QIcon('src/noteApp/NoteAppIcon.ico'))

        try:
            self.setWindowIcon(QIcon('src/noteApp/media/NoteAppIcon.ico'))
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")

        # DB connection
        try:
            self.conn = get_db_connection()
            self.cursor = get_cursor(self.conn)
            QMessageBox.information(self, "Успех", "Подключено к БД.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            sys.exit(1)

        self.user_id = None

        # Bar menu
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # "File"
        file_menu = QMenu("Файл", self)
        self.menu_bar.addMenu(file_menu)
        file_menu.addAction("Вход").triggered.connect(self.login)
        file_menu.addAction("Регистрация").triggered.connect(self.register)
        file_menu.addAction("Выход").triggered.connect(self.logout)
        file_menu.addSeparator()
        file_menu.addAction("Обновить").triggered.connect(self.load_notes)
        file_menu.addAction("Сохранить").triggered.connect(self.save_notes)
        file_menu.addAction("Закрыть").triggered.connect(self.close)

        # Правка - доступна после входа
        self.edit_menu = QMenu("Правка", self)
        self.menu_bar.addMenu(self.edit_menu)
        self.edit_menu.addAction("Добавить заметку").triggered.connect(self.add_note)
        self.edit_menu.addAction("Редактировать").triggered.connect(self.edit_note)
        self.edit_menu.addAction("Удалить").triggered.connect(self.delete_note)
        self.edit_menu.setEnabled(False)

        # Central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Список
        list_tab = QWidget()
        list_layout = QVBoxLayout(list_tab)
        self.notes_list = QListWidget(self)
        list_layout.addWidget(self.notes_list)
        self.notes_list.itemClicked.connect(self.load_selected_note)
        self.tab_widget.addTab(list_tab, "Список")

        # редаткирование
        edit_tab = QWidget()
        form_layout = QVBoxLayout(edit_tab)
        self.title_label = QLabel("Заголовок:", self)
        self.title_edit = QLineEdit(self)
        form_layout.addWidget(self.title_label)
        form_layout.addWidget(self.title_edit)
        self.content_label = QLabel("Содержимое:", self)
        self.content_edit = QTextEdit(self)
        form_layout.addWidget(self.content_label)
        form_layout.addWidget(self.content_edit)
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
        self.tab_widget.addTab(edit_tab, "Редактирование")

        # Дефолт запуск без заметок
        self.settings = QSettings("Company", "NotesApp")
        self.try_auto_login()


    def try_auto_login(self):
        stored_username = self.settings.value("username", None)
        stored_token = self.settings.value("token", None)
        if stored_username and stored_token:
            try:
                self.cursor.execute(
                    "SELECT id FROM users WHERE username = %s AND session_token = %s",
                    (stored_username, stored_token)
                )
                result = self.cursor.fetchone()
                if result:
                    self.user_id = result[0]
                    self.edit_menu.setEnabled(True)
                    self.load_notes()
                    QMessageBox.information(self, "Успех", "Автоматический вход выполнен.")
                    return
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка автоматического входа: {str(e)}")
        # Если не сработало то обычный логин
        self.login()

    def login(self):
        """Вход пользователя."""
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = dialog.username_edit.text().strip()
            password = dialog.password_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                self.cursor.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
                result = self.cursor.fetchone()
                if result:
                    self.user_id = result[0]
                    # Generate and store session token
                    token = str(uuid.uuid4())
                    self.cursor.execute("UPDATE users SET session_token = %s WHERE id = %s", (token, self.user_id))
                    self.conn.commit()
                    # Save to local settings
                    self.settings.setValue("username", username)
                    self.settings.setValue("token", token)
                    self.edit_menu.setEnabled(True)
                    self.load_notes()
                    QMessageBox.information(self, "Успех", "Вход выполнен.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")

    def register(self):
        dialog = RegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = dialog.username_edit.text().strip()
            password = dialog.password_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
                self.conn.commit()
                QMessageBox.information(self, "Успех", "Регистрация завершена. Теперь войдите.")
            except pg_errors.UniqueViolation:
                self.conn.rollback()
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует.")
            except psycopg2.Error as e:
                self.conn.rollback()
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")

    def logout(self):
        if self.user_id:
            try:
                self.cursor.execute("UPDATE users SET session_token = NULL WHERE id = %s", (self.user_id,))
                self.conn.commit()
            except psycopg2.Error as e:
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка выхода: {str(e)}")
        self.settings.remove("username")
        self.settings.remove("token")
        self.user_id = None
        self.edit_menu.setEnabled(False)
        self.notes_list.clear()
        self.clear_form()
        QMessageBox.information(self, "Успех", "Вы вышли из аккаунта.")

    def add_note(self):
        # Работает только после авторизации пользователя
        if not self.user_id:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в аккаунт.")
            return
        try:
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            self.cursor.execute("SELECT COUNT(*) FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
            if self.cursor.fetchone()[0] > 0:
                raise pg_errors.UniqueViolation("Заметка с таким заголовком уже существует.")

            self.cursor.execute(
                "INSERT INTO notes (title, content, user_id) VALUES (%s, %s, %s)",
                (title, content, self.user_id)
            )
            self.conn.commit()
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка добавлена.")
        except pg_errors.UniqueViolation as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except psycopg2.Error as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def edit_note(self):
        if not self.user_id:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в аккаунт.")
            return
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для редактирования.")

            old_title = selected.text()
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            if title != old_title:
                self.cursor.execute("SELECT COUNT(*) FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
                if self.cursor.fetchone()[0] > 0:
                    raise pg_errors.UniqueViolation("Заметка с таким заголовком уже существует.")

            self.cursor.execute(
                "UPDATE notes SET title = %s, content = %s WHERE title = %s AND user_id = %s",
                (title, content, old_title, self.user_id)
            )
            self.conn.commit()
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка обновлена.")
        except pg_errors.UniqueViolation as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except psycopg2.Error as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def delete_note(self):
        if not self.user_id:
            QMessageBox.warning(self, "Ошибка", "Сначала войдите в аккаунт.")
            return
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для удаления.")

            title = selected.text()
            self.cursor.execute("DELETE FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
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
        # загрузка в бд
        if not self.user_id:
            return
        try:
            title = item.text()
            self.cursor.execute("SELECT content FROM notes WHERE title = %s AND user_id = %s", (title, self.user_id))
            content = self.cursor.fetchone()[0]
            self.title_edit.setText(title)
            self.content_edit.setPlainText(content)
            self.tab_widget.setCurrentIndex(1)
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка загрузки: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def update_notes_list(self):
        # обновить список заметок для конкретного пользователя
        try:
            self.notes_list.clear()
            if self.user_id:
                self.cursor.execute("SELECT title FROM notes WHERE user_id = %s ORDER BY created_at DESC", (self.user_id,))
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
        if self.user_id:
            QMessageBox.information(self, "Успех", "Заметки обновлены из БД.")

    def save_notes(self):
        try:
            self.conn.commit()
            if self.user_id:
                QMessageBox.information(self, "Успех", "Изменения сохранены в БД.")
        except psycopg2.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка сохранения: {str(e)}")

    def closeEvent(self, event):
        # Connection off
        self.cursor.close()
        self.conn.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())