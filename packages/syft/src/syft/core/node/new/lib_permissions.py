# stdlib
from enum import Enum

# relative
from .serializable import serializable
from .uid import UID


@serializable()
class CMPCRUDPermission(Enum):
    NONE_EXECUTE = 1
    ALL_EXECUTE = 2


@serializable()
class CMPPermission:
    @property
    def permissions_string(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.permission_string

    @staticmethod
    def all_execute():
        return CMPCompoundPermission(CMPCRUDPermission.ALL_EXECUTE)

    @staticmethod
    def none_execute():
        return CMPCompoundPermission(CMPCRUDPermission.NONE_EXECUTE)


@serializable()
class CMPUserPermission:
    def __init__(self, user_id: UID, permission: CMPCRUDPermission):
        self.user_id = user_id
        self.permissions = permission

    @property
    def permission_string(self) -> str:
        return f"<{self.user_uid}>_{self.permission}"

    def __repr__(self) -> str:
        return self.permission_string


@serializable()
class CMPCompoundPermission:
    def __init__(self, permission: CMPCRUDPermission):
        self.permissions = permission

    @property
    def permission_string(self) -> str:
        return self.permissions.name

    def __repr__(self) -> str:
        return self.permission_string
