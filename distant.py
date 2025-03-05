import sys
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информация о котах")
        self.setGeometry(100, 100, 800, 600)
        self.cat_data = self.fetch_cat_data()
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Origin", "Temperament"])
        
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 440)
        self.populate_table(self.cat_data)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все страны")
        origins = sorted(set(cat['origin'] for cat in self.cat_data))
        self.filter_combo.addItems(origins)
        self.delete_button = QPushButton("Удалить кота")
        self.delete_button.setFixedSize(100, 30)
        
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр по происхождению:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addWidget(self.delete_button)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.table.cellDoubleClicked.connect(self.show_cat_details)
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        self.delete_button.clicked.connect(self.delete_selected_cat)
    
    def fetch_cat_data(self):
        response = requests.get("https://api.thecatapi.com/v1/breeds")
        return response.json()
    
    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row, cat in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(cat['name']))
            self.table.setItem(row, 1, QTableWidgetItem(cat['origin']))
            self.table.setItem(row, 2, QTableWidgetItem(cat['temperament']))
    
    def show_cat_details(self, row, column):
        cat_data = self.cat_data[row]
        dialog = CatDetailDialog(cat_data, self)
        dialog.exec()
        self.filter_table(self.filter_combo.currentText())
    
    def filter_table(self, origin): # Этот метод убирает из таблицы котов, которые не подходят под фильтр
        filtered_data = self.cat_data # Берем всех котов из списка
        if origin != "Все страны": # Если выбрано не "Все страны", а другое значение 
            filtered_data = [cat for cat in self.cat_data if cat['origin'] == origin] # Оставляем котов из выбранной страны
        self.populate_table(filtered_data) # Показываются в таблице только те коты, что подходят под фильтр
    
    def delete_selected_cat(self): # Этот метод убирает кота из списка
        current_row = self.table.currentRow() # Проверка выбрнанной строки
        if current_row >= 0: # Если строка выбрана 
            del self.cat_data[current_row] # Удаление кота из списка по номеру строки
            self.filter_table(self.filter_combo.currentText()) # Обновление таблицы

class CatDetailDialog(QDialog):
    def __init__(self, cat_data, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Подробная информация о коте")
        self.cat_data = cat_data
        self.is_editing = False
        self.setFixedSize(400, 300)
        
        self.layout = QVBoxLayout()
        self.name_label = QLabel(f"Name: {cat_data['name']}")
        self.origin_label = QLabel(f"Origin: {cat_data['origin']}")
        self.temperament_label = QLabel(f"Temperament: {cat_data['temperament']}")
        self.description_label = QLabel(f"Description: {cat_data.get('description', 'Нет описания')}")
        
        self.name_edit = QLineEdit(cat_data['name'])
        self.origin_edit = QLineEdit(cat_data['origin'])
        self.temperament_edit = QLineEdit(cat_data['temperament'])
        self.description_edit = QLineEdit(cat_data.get('description', ''))
        
        self.edit_button = QPushButton("Редактировать")
        self.save_button = QPushButton("Сохранить")
        self.save_button.hide()
        
        self.edit_button.setFixedSize(100, 30)
        self.save_button.setFixedSize(100, 30)
        
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.origin_label)
        self.layout.addWidget(self.origin_edit)
        self.layout.addWidget(self.temperament_label)
        self.layout.addWidget(self.temperament_edit)
        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_edit)
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)
        
        self.edit_button.clicked.connect(self.toggle_edit)
        self.save_button.clicked.connect(self.save_changes)
        
    def toggle_edit(self): # Метод окна редактирования
        self.is_editing = not self.is_editing # смена окон между редактированием и сохранением
        if self.is_editing: # режим редактирования
            self.name_edit.show() # Показываем поле, где можно менять имя
            self.origin_edit.show() # Показываем поле, где можно менять происхождение
            self.temperament_edit.show() # Показываем поле, где можно менять темперамент
            self.description_edit.show() # Показываем поле, где можно менять описание
            self.edit_button.setText("Отмена") # кнопка, чтобы можно было выйти
            self.save_button.show() #
        else:
            self.name_label.show() # текст с именем
            self.origin_label.show() # текст с именем
            self.temperament_label.show() # текст с именем
            self.description_label.show() # текст с именем
            self.edit_button.setText("Редактировать") # возвращение кнопки редактирования
            self.save_button.hide() # убираем кнопку сохранения
     
    def save_changes(self):
        self.cat_data['name'] = self.name_edit.text()
        self.cat_data['origin'] = self.origin_edit.text()
        self.cat_data['temperament'] = self.temperament_edit.text()
        self.cat_data['description'] = self.description_edit.text()
        self.name_label.setText(f"Name: {self.cat_data['name']}")
        self.origin_label.setText(f"Origin: {self.cat_data['origin']}")
        self.temperament_label.setText(f"Temperament: {self.cat_data['temperament']}")
        self.description_label.setText(f"Description: {self.cat_data['description']}")
        self.toggle_edit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
