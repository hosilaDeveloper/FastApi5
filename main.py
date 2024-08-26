from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from database import Session_Local, engine
import models
import schema

app = FastAPI()


# Dependency
def get_db():
    db = Session_Local()
    try:
        yield db
    finally:
        db.close()


# CRUD uchun Category endpointlari
@app.post('/categories/', response_model=schema.Category)
def create_category(category: schema.CategoryCreate, db: Session == Depends(get_db)):
    db_category = models.Category(dict=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get('/categories/', response_model=List[schema.Category])
def read_categories(db: Session == Depends(get_db)):
    return db.query(models.Category).all()


@app.post('/tags/', response_model=schema.Tag)
def create_tag(tag: schema.TagCreate, db: Session == Depends(get_db)):
    db_tag = models.Tag(dict=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get('/tags/', response_model=List[schema.Tag])
def read_tag(db: Session == Depends(get_db)):
    return db.query(models.Tag).all()


@app.post("/posts/", response_model=schema.Post)
def create_post(post: schema.PostCreate, db: Session == Depends(get_db)):
    db_post = models.Post(
        title=post.title,
        description=post.description,
        image=post.image,
        category_id=post.category_id
    )
    db.add(db_post)

    db_post.tags = db.query(models.Tag).filter(models.Tag.id.in_(post.tag_ids)).all()

    db.commit()
    db.refresh(db_post)
    return db_post


@app.get('/products/', response_model=List[schema.Post])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.get("/products/{product_id}", response_model=schema.Post)
def read_post(product_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == product_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail='Post not faund')
    return post


@app.put("/products/{product_id}", response_model=schema.Post)
def update_post(product_id: int, post: schema.PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == product_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Post not found')
    for key, value in post.dict().items():
        setattr(db_post, key, value)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete('/products/{product_id}')
def delete_post(product_id: int, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == product_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail='Product not found')
    db.delete(db_post)
    db.commit()
    return {'message': 'Post delete'}
