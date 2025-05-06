import json
from typing import Any


class FileWorker:
    """
    Класс для работы с файлами
    """
    def create_file(self, file_name: str, content: Any) -> None:
        """
        Создает json-файл и записывает в него сериализованные данные

        Args:
            - file_name(str): наименование json-файла для записи
            - content(Any): объект, сериализуемый в JSON
        """
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                file_type = file_name.split(".")[-1]
                if file_type == "json":
                    json.dump(content, file, indent=4)
                else:
                    file.write(content)
        except IOError as e:
            print(f"Ошибка при формировании json-файла {file_name}: {e}")
            raise

    def read_file(self, file_name: str) -> Any:
        """
        Читает и десериализует json-файл

        Args:
            - file_name(str): наименование json-файла для чтения

        Returns:
            - десериализованные данные из json-файла
        """
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                file_type = file_name.split(".")[-1]
                if file_type == "json":
                    return json.load(file)
                else:
                    return file.read()
        except (IOError, json.JSONDecodeError) as e:
            print(f"Ошибка чтения json-файла {file_name}: {e}")
            raise
file_worker = FileWorker()