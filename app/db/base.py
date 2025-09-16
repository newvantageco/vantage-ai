from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData


class Base(DeclarativeBase):
	metadata = MetaData()



