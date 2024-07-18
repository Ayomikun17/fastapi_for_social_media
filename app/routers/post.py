from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",  # All request start with a /post
    tags=["Posts"],  # Gropuping all the Post routes in the documentation
) 


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # Implementation using SQL
    # cursor.execute("""Select * from posts""")
    # posts = cursor.fetchall()

    # ORM implementation
    # Query parameters
    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute("""Insert into posts(title, content, published)
    # values (%s, %s, %s) returning * """,
    #                (post.title, post.content, post.published))

    # new_post = cursor.fetchone()

    # conn.commit()
    print(current_user.id)
    new_post = models.Post(
        owner_id=current_user.id, **post.model_dump()
    )  # Unpacking the model as a dictionary
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Retrieving so you can see new post created

    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", str(id,))
    # post = cursor.fetchone()
    # print(post)
    # post = find_post(id)

    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute("""DELETE FROM posts
    # WHERE id = %s returning *""", str(id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # cursor.execute("""UPDATE posts SET title =%s, content=%s, published=%s
    # WHERE id = %s returning *""",
    # (post.title, post.content, post.published, str(id,)))
    # update_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()
