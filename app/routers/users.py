from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> models.User:
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário {user_id} não encontrado",
        )
    return user


@router.get("", response_model=list[schemas.UserRead], summary="Lista usuários")
def read_users(
    skip: int = Query(0, ge=0, description="Quantos registros pular"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros retornados"),
    db: Session = Depends(get_db),
):
    return crud.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserRead, summary="Busca um usuário")
def read_user(user: models.User = Depends(get_user_or_404)):
    return user


@router.post(
    "",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um usuário",
)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, payload)


@router.put(
    "/{user_id}",
    response_model=schemas.UserRead,
    summary="Substitui um usuário (todos os campos)",
)
def replace_user(
    payload: schemas.UserCreate,
    user: models.User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    return crud.replace_user(db, user, payload)


@router.patch(
    "/{user_id}",
    response_model=schemas.UserRead,
    summary="Atualiza parcialmente um usuário",
)
def update_user(
    payload: schemas.UserUpdate,
    user: models.User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe ao menos um campo para atualizar",
        )
    return crud.update_user(db, user, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove um usuário",
)
def delete_user(
    user: models.User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    crud.delete_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.head("/{user_id}", status_code=status.HTTP_200_OK, summary="Verifica se existe")
def head_user(user: models.User = Depends(get_user_or_404)):
    return Response(status_code=status.HTTP_200_OK)


@router.options("", summary="Métodos disponíveis na coleção")
def options_users():
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"Allow": "GET, POST, OPTIONS"},
    )
