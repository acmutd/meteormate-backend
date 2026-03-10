from datetime import datetime
from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Banlist(DeclarativeBase):
    __tablename__ = "banlist"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    net_id: Mapped[str] = mapped_column(Text, nullable=False)
    banned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Admins(DeclarativeBase):
    __tablename__ = "admins"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    net_id: Mapped[str] = mapped_column(Text, nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
