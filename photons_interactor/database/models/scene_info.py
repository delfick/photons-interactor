from photons_interactor.database.connection import Base

from sqlalchemy import Column, String, Text


class SceneInfo(Base):
    uuid = Column(String(64), nullable=True, index=True, unique=True)
    label = Column(Text(), nullable=True)
    description = Column(Text(), nullable=True)

    def as_dict(self, ignore=None):
        dct = {"uuid": self.uuid, "label": self.label, "description": self.description}
        return {
            k: v for k, v in dct.items() if v is not None and (ignore is None or k not in ignore)
        }
