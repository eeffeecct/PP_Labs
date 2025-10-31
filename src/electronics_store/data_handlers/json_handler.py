import json
from pathlib import Path

from ..exceptions.custom_exceptions import DataValidationError


class JSONHandler:
    @staticmethod
    def read_file(file_path: str) -> dict:
        path = Path(file_path)
        if not path.exists():
            return {"products": [], "customers": [], "orders": [], "metadata": {}}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON in {file_path}: {e}")

    @staticmethod
    def write_file(data: dict, file_path: str) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def validate_json_schema(data: dict, expected_structure: dict) -> bool:
        for key, expected_type in expected_structure.items():
            if key not in data:
                raise DataValidationError(f"Missing field: {key}")
            if not isinstance(data[key], expected_type):
                raise DataValidationError(f"Field '{key}' should be {expected_type}")
        return True