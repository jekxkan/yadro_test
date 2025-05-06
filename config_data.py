from typing import Dict, Any


class ConfigData:
    def find_differences(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) \
            -> Dict[str, list]:
        """
        Метод ищет разницу между старой конфигурацией и ее новой версией

        Args:
            - old_config(Dict[str]): старая конфигурация
            - new_config(Dict[str]): новый вариант конфигурации

        Returns:
            - diff_config(Dict[str, list]): словарь, с типом изменений и пармамметрами,
                                            которые были подвергнуты ему
        """

        diff_config = {
            "additions": [],
            "deletions": [],
            "updates": []
        }
        # Создаем множества,чтобы можно было производить операции -, +, &
        old_params = set(old_config.keys())
        new_params = set(new_config.keys())

        # Новые параметры
        for key in new_params - old_params:
            info = {
                "key": key,
                "value": new_config[key]
            }
            diff_config["additions"].append(info)

        # Удаленые параметры
        for key in old_params - new_params:
            diff_config["deletions"].append(key)

        # Обновленные параметры
        for key in old_params & new_params:
            if old_config[key] != new_config[key]:
                info = {
                    "key": key,
                    "from": old_config[key],
                    "to": new_config[key]
                }
                diff_config["updates"].append(info)

        return diff_config


    def do_config_changes(self, old_config: Dict[str, Any], diff_config: Dict[str, Any]) \
            -> Dict[str, Any]:
        """
        Создает файл, к которому были применены изменения конфигурации

        Args:
            - old_config(json): старая конфигурация
            - diff_config(json): json отражающий измененения с их типами

        Returns:
            - new_json(json): новая конфигурация о внесеными изменениями
        """

        new_json = {}

        # Обрабатываем добавленные параметры
        for addition in diff_config.get("additions", []):
            key = addition["key"]
            value = addition["value"]
            if key:
                new_json[key] = value

        # Обрабатываем обновленные параметры
        for update in diff_config.get("updates", []):
            key = update["key"]
            new_value = update["to"]
            if key:
                new_json[key] = new_value

        # Обрабатываем параметры, которые не были подвергнуты изменениям
        unchanged_params = set(old_config) - set(new_json) - set(diff_config.get("deletions", []))
        for param in unchanged_params:
            new_json[param] = old_config[param]

        return new_json

config_data_worker = ConfigData()