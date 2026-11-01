from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from dependencies import SessionDep
from models import Url
from schemas import UrlCreate, UrlResponse
from utils import code_generator

router = APIRouter()


@router.get("/")
def root():
    return {"message": "api is running"}


@router.post("/urls", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_url(session: SessionDep, url_create: UrlCreate):
    for _ in range(5):
        url = Url(
            real_url=str(url_create.real_url),
            expires_at=url_create.expires_at,
            code=code_generator(),
        )
        session.add(url)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            continue
        else:
            session.commit()
            session.refresh(url)
            return url

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Unable to generate unique code. Try again",
    )


@router.get("/urls", response_model=list[UrlResponse])
def read_urls(session: SessionDep):
    statement = select(Url)
    return session.scalars(statement).all()


@router.get("/urls/{url_id}", response_model=UrlResponse)
def read_url(session: SessionDep, url_id: int):
    url = session.get(Url, url_id)

    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )

    return url


@router.delete("/urls/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(session: SessionDep, url_id: int):
    url = session.get(Url, url_id)

    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )

    session.delete(url)
    session.commit()
