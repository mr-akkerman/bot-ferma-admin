import os

def test_project_structure():
    """Тест для проверки наличия всех необходимых файлов и папок проекта"""
    
    # Список файлов и папок для проверки
    required_files = [
        'app.py',
        'models.py', 
        'auth.py',
        'requirements.txt',
        'static/css/style.css'
    ]
    
    required_directories = [
        'templates',
        'static',
        'static/css'
    ]
    
    # Проверка файлов
    print("Проверка файлов:")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - найден")
        else:
            print(f"✗ {file_path} - НЕ НАЙДЕН")
    
    # Проверка папок
    print("\nПроверка папок:")
    for dir_path in required_directories:
        if os.path.isdir(dir_path):
            print(f"✓ {dir_path}/ - найдена")
        else:
            print(f"✗ {dir_path}/ - НЕ НАЙДЕНА")
    
    print("\nТест структуры проекта завершен!")

if __name__ == "__main__":
    test_project_structure()
