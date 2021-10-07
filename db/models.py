from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    func,
    TIMESTAMP,

)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_serializer import SerializerMixin

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class Tokens(Base):
    __tablename__ = "tokens"

    id = Column("id", Integer, primary_key=True)
    access_token = Column("access_token", String)
    refresh_token = Column("refresh_token", String)
    access_expires_at = Column("timestamp", TIMESTAMP(timezone=False), nullable=False)


user_task_table = Table(
    "user_task",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE")),
    Column("task_id", Integer, ForeignKey("task.id", ondelete="CASCADE")),
    UniqueConstraint("user_id", "task_id", name="uix_1"),
)


class User(Base):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True)
    strava_id = Column("strava_id", Integer)
    token = Column(
        "token_id", ForeignKey("tokens.id", ondelete="CASCADE")
    )
    mileage = Column("mileage", Integer)
    created_at = Column(
        "created_at", DateTime, server_default=func.now(), nullable=False
    )
    updated_at = Column(
        "updated_at",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    tasks = relationship("Task", secondary=user_task_table)


class Task(Base, SerializerMixin):
    __tablename__ = "task"

    serialize_only = ('name', 'every', 'comment')

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    every = Column("every", Integer)
    comment = Column("comment", String)


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column("id", Integer, primary_key=True)
    user_id = Column(
        "user_id", ForeignKey("user.id", ondelete="CASCADE")
    )
    task_id = Column(
        "task_id", ForeignKey("task.id", ondelete="CASCADE")
    )
    diff = Column("diff", Integer)


class StravaEvent(Base):
    __tablename__ = "strava_event"

    id = Column("id", Integer, primary_key=True)
    user_id = Column(
        "user_id", ForeignKey("user.id", ondelete="CASCADE")
    )
    event_km = Column("event_km", Integer)
    event_time = Column("event_time", TIMESTAMP(timezone=False), nullable=False)



