import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

import yaml

from utils.singleton import SingletonMeta

_CONFIG_DIR = Path(__file__).parent.parent / "configuration"
_ENV_VAR_PREFIX = "TEST_"


class BaseHelper(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._cache = {}

    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        try:
            with file_path.open(mode="r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse YAML file: {file_path}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to load YAML file: {file_path}") from e

    def _read_file(self, file_path: Path, cache_key: str) -> Dict[str, Any]:
        if cache_key not in self._cache:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            self._cache[cache_key] = self._load_yaml(file_path)
        return self._cache[cache_key]


class ElementHelper(BaseHelper):
    def read(self, file_name: str) -> Dict[str, Any]:
        base_path = Path(__file__).parent.parent / "elements"
        file_path = base_path / f"{file_name}.yaml"
        cache_key = f"element_{file_name}"
        return self._read_file(file_path, cache_key)


class ConfigHelper(BaseHelper):
    def __init__(self, env: str = "default") -> None:
        super().__init__()
        if not hasattr(self, "_data"):
            self._data = self._build_config(env)

    def _build_config(self, env: str) -> Dict[str, Any]:
        default = self._read_file(_CONFIG_DIR / "default.yaml", "config_default")
        merged = deepcopy(default)

        if env != "default":
            env_file = _CONFIG_DIR / f"{env}.yaml"
            if env_file.exists():
                env_config = self._read_file(env_file, f"config_{env}")
                self._deep_merge(merged, env_config)
            else:
                raise Exception("Invalid environment, please check again")

        self._apply_env_vars(merged)
        return merged

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> None:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigHelper._deep_merge(base[key], value)
            else:
                base[key] = value

    @staticmethod
    def _apply_env_vars(data: Dict, prefix: str = _ENV_VAR_PREFIX) -> None:
        """Override config values with environment variables.

        Mapping: TEST_YOUTUBE__ENTRY_URL -> data["youtube"]["entry_url"]
        - prefix is stripped
        - double underscore (__) splits into nested keys
        - keys are lowercased
        """
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue
            parts = env_key[len(prefix) :].lower().split("__")
            target = data
            for part in parts[:-1]:
                if part not in target or not isinstance(target[part], dict):
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = env_value

    def get(self, category: str) -> Dict[str, Any]:
        if category not in self._data:
            raise KeyError(f"Config category '{category}' not found")
        return self._data[category]

    @property
    def all(self) -> Dict[str, Any]:
        return self._data
