from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy_utils import PasswordType
from .base import Base
from datetime import datetime

# Role-Permission association table
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(PasswordType(
        schemes=['pbkdf2_sha512', 'md5_crypt'],
        deprecated=['md5_crypt']
    ))
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Access control
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        backref="roles"
    )

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255)) 