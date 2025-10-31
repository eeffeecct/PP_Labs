import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from pathlib import Path

from ..exceptions.custom_exceptions import DataValidationError


class XMLHandler:

    @staticmethod
    def read_file(file_path: str) -> ET.Element:
        path = Path(file_path)
        if not path.exists():
            raise DataValidationError(f"File not found: {file_path}")

        try:
            return ET.parse(file_path).getroot()
        except ET.ParseError as e:
            raise DataValidationError(f"Invalid XML in {file_path}: {e}")

    @staticmethod
    def write_file(data: ET.Element, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        rough_string = ET.tostring(data, encoding='utf-8')
        pretty_xml = minidom.parseString(rough_string).toprettyxml(indent="  ")

        # Убираем пустые строки
        pretty_xml = '\n'.join(line for line in pretty_xml.split('\n') if line.strip())

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(pretty_xml)

    @staticmethod
    def dict_to_xml_element(tag: str, data: dict) -> ET.Element:
        element = ET.Element(tag)

        for key, value in data.items():
            if isinstance(value, dict):
                element.append(XMLHandler.dict_to_xml_element(key, value))
            elif isinstance(value, list):
                for item in value:
                    child_tag = key[:-1] if key.endswith('s') else key
                    if isinstance(item, dict):
                        element.append(XMLHandler.dict_to_xml_element(child_tag, item))
                    else:
                        child = ET.Element(key)
                        child.text = str(item)
                        element.append(child)
            else:
                child = ET.Element(key)
                child.text = str(value)
                element.append(child)

        return element

    @staticmethod
    def xml_element_to_dict(element: ET.Element) -> dict:
        return {
            child.tag: child.text if len(child) == 0
            else XMLHandler.xml_element_to_dict(child)
            for child in element
        }