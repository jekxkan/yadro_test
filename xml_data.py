import xml.etree.ElementTree as ET
from abc import abstractmethod, ABC
from typing import List, Dict


class IXMLComponent(ABC):
    """
    Абстрактный класс, от которого наследуется XMLComposite.
    Гарантирует, что у каждого объекта XMLComposite есть метод to_xml,
    который формирует xml-строки
    """
    @abstractmethod
    def to_xml(self, indent: int = 0) -> str:
        pass


class XMLComposite(IXMLComponent):
    """
    Класс, представляющий элемент xml-структуры

    Attributes:
        - name(str): наименование тега
        - attribute_value(str): содержимое атрибутов(их тип). По умолчаю None, так как
                                у класов нет типов, а объект XMLComposite предназначен и
                                для классов и для их атрибутов
        - children(List['XMLComposite']): дочерние элементы

    Методы позволяют рекурсивно формировать строковое представление xml с отступами
    """
    def __init__(self, name: str, attribute_value: str = None):
        self.name = name
        self.attribute_value = attribute_value
        self.children: List['XMLComposite'] = []

    def add(self, component: 'XMLComposite'):
        self.children.append(component)

    def to_xml(self, indent: int = 0) -> str:
        """
        Рекурсивно формирует xml-строку с отступами

        Логика форматирования:
        - Если есть дочерние элементы, открывающий и закрывающий теги на отдельных строках и
         дочерние элементы с увеличенным отступом
        - Если есть атрибуты, то они выводятся в одной строке с их типом
        - Если элемент пустой, выводятся открывающий и закрывающий теги на отдельных строках

        Args:
            - indent(int): отступа

        Returns:
            - отформатированная xml-строка для данного и его дочерних элементов
        """
        indent_str = "    " * indent

        if self.children:
            # Если у класса есть дочерние классы, то добавляем открывающий тег
            lines = [f"{indent_str}<{self.name}>"]
            for child in self.children:
                lines.append(child.to_xml(indent + 1))
            lines.append(f"{indent_str}</{self.name}>")
            return "\n".join(lines)
        elif self.attribute_value:
            # Если у класса есть атрибуты, то добавляем их на той же строке
            return f"{indent_str}<{self.name}>{self.attribute_value}</{self.name}>"
        else:
            # Если класс пустой (без атрибутов и дочерних классов), то только теги
            return f"{indent_str}<{self.name}>\n{indent_str}</{self.name}>"


class XMLBuilder:
    """
    Класс для построения xml-структуры из json-описания классов

    Принимает список словарей с описанием классов и их атрибутов,
    находит корневой класс и рекурсивно строит дерево XMLComposite

    Использует XMLComposite для представления элементов xml
    """
    def __init__(self, json_data: List[Dict]):
        self.data = {item['class']: item for item in json_data}
        self.root = self._find_root()

    def build(self) -> str:
        """
        Строит xml-строку, начиная с корневого класса

        Returns:
             - xml-строка, представляющая всю структуру
        """
        root_component = self._build_component_obj(self.root['class'])
        return root_component.to_xml(indent=0)

    def _find_root(self) -> Dict:
        """
        Находит корневой класс

        Returns:
            - словарь с описанием корневого класса
        """
        for item in self.data.values():
            if item['isRoot']:
                return item

    def _build_component_obj(self, class_name: str) -> XMLComposite:
        """
        Рекурсивно строит объект XMLComposite для заданного класса

        Args:
            - class_name(str): имя класса для построения

        Returns:
            - объект XMLComposite, представляющий класс и его атрибуты
        """
        component = XMLComposite(class_name)
        for param in self.data[class_name]['parameters']:
            if param['type'] == 'class':
                child_component = self._build_component_obj(param['name'])
                component.add(child_component)
            else:
                attr = XMLComposite(param['name'], param['type'])
                component.add(attr)
        return component


class XMLParser:
    """
    Класс для парсинга xml-файла с описанием классов и агрегаций,
    и преобразования его в список словарей

    Attributes:
        - xml_path (str): путь к xml-файлу для парсинга
        - _classes (Dict[str, Dict]): словарь с описанием классов для использоания
                                      внутри класса, где ключ - имя класса,
                                      значение - словарь с его параметрами
        - _aggregations (List[Dict]): список агрегаций между классами для использоания
                                      внутри класса
    """
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self._classes: Dict[str, Dict] = {}
        self._aggregations: List[Dict] = []

    def parse(self) -> List[Dict]:
        """
        Основной метод для парсинга xml-файла. Разбирает файл и
        извекает из него классы, атрибуты и агригации

        Returns:
            List[Dict]: список словарей, каждый из которых описывает класс,
            включая атрибуты и связи с другими классами
        """
        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        # Парсинг классов
        for elem in root.findall('Class'):
            class_data = {
                'class': elem.get('name'),
                'documentation': elem.get('documentation', ''),
                'isRoot': elem.get('isRoot', 'false').lower() == 'true',
                'parameters': [
                    {'name': a.get('name'), 'type': a.get('type')}
                    for a in elem.findall('Attribute')
                ]
            }
            self._classes[class_data['class']] = class_data

        # Парсинг агрегаций
        for elem in root.findall('Aggregation'):
            multiplicity = elem.get('sourceMultiplicity', '')
            agg = {
                'source': elem.get('source'),
                'target': elem.get('target'),
                'min': multiplicity.split('..')[0] if '..' in multiplicity else multiplicity,
                'max': multiplicity.split('..')[1] if '..' in multiplicity else multiplicity
            }
            self._aggregations.append(agg)

        # Выстраиваем зависимости
        self._resolve_relationships()

        return list(self._classes.values())

    def _resolve_relationships(self):
        """
        Обрабатывает агрегации, связывая классы

        Для каждой агрегации:
        - Добавляет в параметры целевого класса его дочерний класс с типом 'class'
        - Добавляет значения min и max для исходного класса
        """
        for agg in self._aggregations:
            if agg['target'] in self._classes:
                self._classes[agg['target']]['parameters'].append({
                    'name': agg['source'],
                    'type': 'class'
                })
            if agg['source'] in self._classes:
                self._classes[agg['source']].update({
                    'min': agg['min'],
                    'max': agg['max']
                })