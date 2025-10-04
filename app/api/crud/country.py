from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.country import Country
from models.event_log import EventLog
from schemas.country import CountryCreate, CountryUpdate


class RequestInfo:
    """リクエスト情報を保持するデータクラス"""
    def __init__(
        self,
        method: str,
        path: str,
        body: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        self.method = method
        self.path = path
        self.body = body
        self.ip_address = ip_address
        self.user_id = user_id
        self.status_code = status_code


async def create_country(
    db: AsyncSession,
    country_data: CountryCreate,
    request_info: RequestInfo
) -> Country:
    """
    国を作成し、イベントログを記録（Transactional Outboxパターン）

    Args:
        db: データベースセッション
        country_data: 国作成データ
        request_info: リクエスト情報

    Returns:
        作成された国

    Raises:
        IntegrityError: 国コードが重複している場合
    """
    # 1. ビジネスデータの作成
    country = Country(
        name=country_data.name,
        code=country_data.code
    )
    db.add(country)
    await db.flush()  # IDを確定

    # 2. イベントログの記録
    event_log = EventLog(
        event_type="CREATE",
        entity_type="country",
        entity_id=country.id,
        request_method=request_info.method,
        request_path=request_info.path,
        request_body=request_info.body,
        user_id=request_info.user_id,
        ip_address=request_info.ip_address,
        status_code=request_info.status_code,
        processing_status="completed"
    )
    db.add(event_log)
    await db.commit()  # 両方まとめてコミット

    await db.refresh(country)
    return country


async def get_country(db: AsyncSession, country_id: int) -> Optional[Country]:
    """
    国を取得

    Args:
        db: データベースセッション
        country_id: 国ID

    Returns:
        国 (存在しない場合はNone)
    """
    result = await db.execute(
        select(Country).where(Country.id == country_id)
    )
    return result.scalar_one_or_none()


async def get_countries(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Country]:
    """
    国の一覧を取得（ページネーション対応）

    Args:
        db: データベースセッション
        skip: スキップする件数
        limit: 取得する最大件数

    Returns:
        国のリスト
    """
    result = await db.execute(
        select(Country).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def update_country(
    db: AsyncSession,
    country_id: int,
    country_data: CountryUpdate,
    request_info: RequestInfo
) -> Optional[Country]:
    """
    国を更新し、イベントログを記録（Transactional Outboxパターン）

    Args:
        db: データベースセッション
        country_id: 国ID
        country_data: 国更新データ
        request_info: リクエスト情報

    Returns:
        更新された国 (存在しない場合はNone)

    Raises:
        IntegrityError: 国コードが重複している場合
    """
    # 対象の国を取得
    result = await db.execute(
        select(Country).where(Country.id == country_id)
    )
    country = result.scalar_one_or_none()

    if country is None:
        return None

    # 1. ビジネスデータの更新
    if country_data.name is not None:
        country.name = country_data.name
    if country_data.code is not None:
        country.code = country_data.code

    await db.flush()  # 変更を確定

    # 2. イベントログの記録
    event_log = EventLog(
        event_type="UPDATE",
        entity_type="country",
        entity_id=country.id,
        request_method=request_info.method,
        request_path=request_info.path,
        request_body=request_info.body,
        user_id=request_info.user_id,
        ip_address=request_info.ip_address,
        status_code=request_info.status_code,
        processing_status="completed"
    )
    db.add(event_log)
    await db.commit()  # 両方まとめてコミット

    await db.refresh(country)
    return country


async def delete_country(
    db: AsyncSession,
    country_id: int,
    request_info: RequestInfo
) -> Optional[Country]:
    """
    国を削除し、イベントログを記録（Transactional Outboxパターン）

    Args:
        db: データベースセッション
        country_id: 国ID
        request_info: リクエスト情報

    Returns:
        削除された国 (存在しない場合はNone)
    """
    # 対象の国を取得
    result = await db.execute(
        select(Country).where(Country.id == country_id)
    )
    country = result.scalar_one_or_none()

    if country is None:
        return None

    # 1. イベントログの記録（削除前にIDを記録）
    event_log = EventLog(
        event_type="DELETE",
        entity_type="country",
        entity_id=country.id,
        request_method=request_info.method,
        request_path=request_info.path,
        request_body=request_info.body,
        user_id=request_info.user_id,
        ip_address=request_info.ip_address,
        status_code=request_info.status_code,
        processing_status="completed"
    )
    db.add(event_log)

    # 2. ビジネスデータの削除
    await db.delete(country)
    await db.commit()  # 両方まとめてコミット

    return country
