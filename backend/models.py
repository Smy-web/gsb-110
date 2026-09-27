from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Temple(Base):
    __tablename__ = "temples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    location = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    halls = relationship("Hall", back_populates="temple")


class Hall(Base):
    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)
    temple_id = Column(Integer, ForeignKey("temples.id"))
    name = Column(String(255), index=True)
    description = Column(Text)
    damage_details = Column(JSON)
    repair_plan = Column(JSON)
    estimated_cost = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    temple = relationship("Temple", back_populates="halls")
    meetings = relationship("Meeting", back_populates="hall")


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    hall_id = Column(Integer, ForeignKey("halls.id"))
    title = Column(String(255))
    date = Column(DateTime)
    participants = Column(JSON)
    status = Column(String(50), default="pending")
    audio_file_path = Column(String(500))
    transcript = Column(Text)
    speaker_diarization = Column(JSON)
    summary = Column(Text)
    fundraising_copy = Column(Text)
    merit_list = Column(Text)
    markdown_file = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hall = relationship("Hall", back_populates="meetings")
    dialogue_turns = relationship("DialogueTurn", back_populates="meeting")


class DialogueTurn(Base):
    __tablename__ = "dialogue_turns"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    speaker = Column(String(100))
    speaker_role = Column(String(50))
    content = Column(Text)
    timestamp = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="dialogue_turns")


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    amount = Column(String(100))
    blessing_content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
