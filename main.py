from file import file_worker
from xml_data import XMLParser, XMLBuilder
from config_data import config_data_worker


if __name__ == '__main__':
    # Читаем и парсим данные из impulse_test_input.xml
    parser = XMLParser("input/impulse_test_input.xml")
    json_data = parser.parse()

    # Строим xml-структуру, отражающую влоденность классов, а также их атрибуты
    builder = XMLBuilder(json_data)
    xml_structure = builder.build()

    file_worker.create_file("out/meta.json", json_data)
    file_worker.create_file("out/config.xml", xml_structure)

    old_data = file_worker.read_file("input/config.json")
    new_data = file_worker.read_file("input/patched_config.json")

    # Ищем изменения в новой конфигурации
    diff = config_data_worker.find_differences(old_data, new_data)
    file_worker.create_file("out/delta.json", diff)

    # Применяем изменения к конфигурации
    result = config_data_worker.do_config_changes(old_data, diff)
    file_worker.create_file("out/res_patched_config.json", result)
