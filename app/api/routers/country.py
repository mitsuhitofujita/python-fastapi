import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import (
    RequestInfo,
    create_country,
    delete_country,
    get_countries,
    get_country,
    update_country,
)
from database import get_db
from schemas.country import CountryCreate, CountryResponse, CountryUpdate

router = APIRouter(prefix="/countries", tags=["countries"])


def get_client_ip(request: Request) -> str:
    """クライアントIPアドレスを取得"""
    # X-Forwarded-For ヘッダーをチェック (プロキシ経由の場合)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # 直接接続の場合
    return request.client.host if request.client else "unknown"


@router.post(
    "/",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="国を作成",
    description="新しい国を作成し、イベントログを記録します",
)
async def create_country_endpoint(
    country: CountryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPIの依存性注入パターン
):
    """
    国を作成

    - **name**: 国名 (1-100文字)
    - **code**: ISO 3166-1 alpha-2 国コード (2文字、自動的に大文字変換)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(country.model_dump()),
        ip_address=get_client_ip(request),
        status_code=201,
    )

    try:
        created_country = await create_country(db, country, request_info)
        return created_country
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country with code '{country.code}' already exists",
        ) from e


@router.get(
    "/{country_id}",
    response_model=CountryResponse,
    summary="国を取得",
    description="指定されたIDの国を取得します",
)
async def read_country(
    country_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPIの依存性注入パターン
):
    """
    IDで国を取得

    - **country_id**: 国のID
    """
    country = await get_country(db, country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found",
        )
    return country


@router.get(
    "/",
    response_model=list[CountryResponse],
    summary="国の一覧を取得",
    description="国の一覧を取得します (ページネーション対応)",
)
async def read_countries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPIの依存性注入パターン
):
    """
    国の一覧を取得

    - **skip**: スキップする件数 (デフォルト: 0)
    - **limit**: 取得する最大件数 (デフォルト: 100)
    """
    countries = await get_countries(db, skip=skip, limit=limit)
    return countries


@router.put(
    "/{country_id}",
    response_model=CountryResponse,
    summary="国を更新",
    description="指定されたIDの国を更新し、イベントログを記録します",
)
async def update_country_endpoint(
    country_id: int,
    country: CountryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPIの依存性注入パターン
):
    """
    国を更新

    - **country_id**: 国のID
    - **name**: 国名 (オプション)
    - **code**: ISO 3166-1 alpha-2 国コード (オプション、自動的に大文字変換)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(country.model_dump(exclude_unset=True)),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    try:
        updated_country = await update_country(db, country_id, country, request_info)
        if updated_country is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with id {country_id} not found",
            )
        return updated_country
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Country with code '{country.code}' already exists",
        ) from e


@router.delete(
    "/{country_id}",
    response_model=CountryResponse,
    summary="国を削除",
    description="指定されたIDの国を削除し、イベントログを記録します",
)
async def delete_country_endpoint(
    country_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPIの依存性注入パターン
):
    """
    国を削除

    - **country_id**: 国のID
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    deleted_country = await delete_country(db, country_id, request_info)
    if deleted_country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found",
        )
    return deleted_country
