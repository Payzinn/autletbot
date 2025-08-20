from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from datetime import date
from ..db import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    referral_link = Column(ForeignKey("referrals.id"), nullable=True)
    invite_link = Column(String, nullable=True)
    invited_by = Column(String, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
