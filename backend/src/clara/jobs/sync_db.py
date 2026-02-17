from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from clara.config import get_settings

_sync_url = str(get_settings().database_url)
sync_engine = create_engine(_sync_url)
SyncSession = sessionmaker(sync_engine)


def get_sync_session() -> Session:
    return SyncSession()
