from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey, Enum
import enum
from sqlalchemy.orm import relationship
import datetime
from datetime import date
from ..db import Base

class SubscriptionType(enum.Enum):
    BASE = "base"
    TRIAL = "trial"

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    type_sub = Column(Enum(SubscriptionType), nullable=False)
    referral_link_used = Column(String)
    created_at = Column(DateTime)
    expires_at = Column(DateTime)
