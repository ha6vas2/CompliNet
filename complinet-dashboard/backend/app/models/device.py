from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    host = Column(String, unique=True, index=True)
    device_type = Column(String)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Device(name={self.name}, host={self.host}, device_type={self.device_type}, is_active={self.is_active})>"