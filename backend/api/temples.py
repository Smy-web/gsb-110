from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/temples", tags=["寺庙管理"])


@router.post("/", response_model=schemas.Temple)
def create_temple(temple: schemas.TempleCreate, db: Session = Depends(get_db)):
    db_temple = models.Temple(
        name=temple.name,
        location=temple.location,
        description=temple.description,
    )
    db.add(db_temple)
    db.commit()
    db.refresh(db_temple)
    return db_temple


@router.get("/", response_model=List[schemas.Temple])
def get_temples(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    temples = db.query(models.Temple).offset(skip).limit(limit).all()
    return temples


@router.get("/{temple_id}", response_model=schemas.Temple)
def get_temple(temple_id: int, db: Session = Depends(get_db)):
    temple = db.query(models.Temple).filter(models.Temple.id == temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail="寺庙不存在")
    return temple


@router.post("/{temple_id}/halls", response_model=schemas.Hall)
def create_hall(temple_id: int, hall: schemas.HallCreate, db: Session = Depends(get_db)):
    temple = db.query(models.Temple).filter(models.Temple.id == temple_id).first()
    if not temple:
        raise HTTPException(status_code=404, detail="寺庙不存在")
    
    db_hall = models.Hall(
        temple_id=temple_id,
        name=hall.name,
        description=hall.description,
        damage_details=hall.damage_details,
        repair_plan=hall.repair_plan,
        estimated_cost=hall.estimated_cost,
    )
    db.add(db_hall)
    db.commit()
    db.refresh(db_hall)
    return db_hall


@router.get("/{temple_id}/halls", response_model=List[schemas.Hall])
def get_temple_halls(temple_id: int, db: Session = Depends(get_db)):
    halls = db.query(models.Hall).filter(models.Hall.temple_id == temple_id).all()
    return halls


@router.get("/halls/{hall_id}", response_model=schemas.Hall)
def get_hall(hall_id: int, db: Session = Depends(get_db)):
    hall = db.query(models.Hall).filter(models.Hall.id == hall_id).first()
    if not hall:
        raise HTTPException(status_code=404, detail="殿堂不存在")
    return hall


@router.put("/halls/{hall_id}", response_model=schemas.Hall)
def update_hall(hall_id: int, hall_update: schemas.HallCreate, db: Session = Depends(get_db)):
    db_hall = db.query(models.Hall).filter(models.Hall.id == hall_id).first()
    if not db_hall:
        raise HTTPException(status_code=404, detail="殿堂不存在")
    
    for key, value in hall_update.model_dump().items():
        setattr(db_hall, key, value)
    
    db.commit()
    db.refresh(db_hall)
    return db_hall
