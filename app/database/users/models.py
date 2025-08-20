from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import datetime
from datetime import date
from ..db import Base
from enum import Enum as PyEnum

class UserStatus(PyEnum):
    ADMIN = 'active'
    USER = 'user'

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    referral_id = Column(Integer, ForeignKey("referrals.id", ondelete="SET NULL"), nullable=True)
    invite_link = Column(String, nullable=True)
    invited_by = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.USER)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    referrals = relationship("Referrals", backref="user", cascade="all, delete", foreign_keys="Referrals.user_id" )
