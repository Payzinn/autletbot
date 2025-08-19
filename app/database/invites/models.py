from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from datetime import date
from ..db import Base


class Invite(Base):
    __tablename__ = "invites"
    id = Column(Integer, primary_key=True)
    owner_id = Column(ForeignKey("users.id"))
    invite_link = Column(String)
    qr_code_path = Column(String)
    created_at = Column(DateTime)
    unique_code = Column(String, nullable=True)