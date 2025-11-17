import sys

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

        # Временно до ДБ данные будут здесь
        self.notes = []  # {'title': str, 'content': str}

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # вертикальный макет
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

    def add_note(self):
        try:
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            for note in self.notes:
                if note['title'].lower() == title.lower():
                    raise ValueError("Заметка с таким заголовком уже существует.")

            self.notes.append({'title': title, 'content': content})
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка добавлена.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def edit_note(self):
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для редактирования.")

            index = self.notes_list.row(selected)
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            if not title or not content:
                raise ValueError("Заголовок и содержимое не могут быть пустыми.")

            self.notes[index] = {'title': title, 'content': content}
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка обновлена.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def delete_note(self):
        try:
            selected = self.notes_list.currentItem()
            if not selected:
                raise ValueError("Выберите заметку для удаления.")

            index = self.notes_list.row(selected)
            del self.notes[index]
            self.update_notes_list()
            self.clear_form()
            QMessageBox.information(self, "Успех", "Заметка удалена.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def load_selected_note(self, item):
        try:
            index = self.notes_list.row(item)
            note = self.notes[index]
            self.title_edit.setText(note['title'])
            self.content_edit.setPlainText(note['content'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")

    def update_notes_list(self):
        self.notes_list.clear()
        for note in self.notes:
            self.notes_list.addItem(note['title'])

    def clear_form(self):
        self.title_edit.clear()
        self.content_edit.clear()

    def load_notes(self):
        """Загрузка заметок (заглушка)"""
        QMessageBox.information(self, "Инфо", "Функция загрузки из БД будет добавлена позже.")

    def save_notes(self):
        """Сохранение заметок (заглушка)"""
        QMessageBox.information(self, "Инфо", "Функция сохранения в БД будет добавлена позже.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())