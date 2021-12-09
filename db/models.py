from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    func,
    TIMESTAMP,

)
from sqlalchemy.orm import declarative_base
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
    apns_token = Column("apns_token", String)


class User(Base):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True)
    strava_id = Column("strava_id", Integer)
    token_id = Column(
        "token_id", ForeignKey("tokens.id", ondelete="CASCADE")
    )
    mileage = Column("mileage", Integer, default=0)
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


class Task(Base, SerializerMixin):
    __tablename__ = "task"

    serialize_only = ('name', 'every', 'comment')

    id = Column("id", Integer, primary_key=True)
    user = Column(
        "user_id", ForeignKey("user.id", ondelete="CASCADE")
    )
    name = Column("name", String)
    every = Column("every", Integer)
    comment = Column("comment", String)
    remain = Column("remain", Integer, default=0)


class Notifications(Base):
    __tablename__ = "notifications"

    id = Column("id", Integer, primary_key=True)
    user_id = Column(
        "user_id", ForeignKey("user.id", ondelete="CASCADE")
    )
    task_id = Column(
        "task_id", ForeignKey("task.id", ondelete="CASCADE")
    )


class StravaEvent(Base):
    __tablename__ = "strava_event"

    id = Column("id", Integer, primary_key=True)
    user_id = Column(
        "user_id", ForeignKey("user.id", ondelete="CASCADE")
    )
    distance = Column("distance", Integer)
    event_time = Column("event_time", TIMESTAMP(timezone=False), nullable=False)



