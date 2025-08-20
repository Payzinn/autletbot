from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
import datetime
from datetime import date
from ..db import Base
from enum import Enum as PyEnum

class ReferralStatus(PyEnum):
    ACTIVE = 'active'
    DISABLED = 'disabled'


class Referrals(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger,ForeignKey("users.id"))
    referral_link = Column(String)
    status = Column(Enum(ReferralStatus))