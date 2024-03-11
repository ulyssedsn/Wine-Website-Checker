from importlib import import_module
from re import sub


class Factory:
    @classmethod
    def _module_name(cls, factory_key, class_name):
        submodule = f"{sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()}"
        return '.'.join(
            __name__.split('.')[:-1] + [factory_key.lower(), submodule])

    @classmethod
    def instance(cls, factory_key, message, user, request_session=None):
        try:
            class_name = ''.join(part.capitalize() for part in message.split(
                '_'))
            module_name = cls._module_name(factory_key, class_name)
            return getattr(import_module(module_name), class_name)(
                request_session, user)
        except ModuleNotFoundError:
            raise Exception('Module not found')
        except AttributeError:
            raise Exception(f"Error importing {module_name}.{class_name}")
