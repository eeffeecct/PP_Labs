import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu

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
        file_menu.addAction("Открыть")
        file_menu.addAction("Сохранить")
        file_menu.addAction("Выход")

        edit_menu = QMenu("Правка", self)
        self.menu_bar.addMenu(edit_menu)
        edit_menu.addAction("Добавить заметку")
        edit_menu.addAction("Редактировать")
        edit_menu.addAction("Удалить")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.show()
    sys.exit(app.exec())