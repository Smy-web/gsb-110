from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/donors", tags=["功德主管理"])


@router.post("/", response_model=schemas.Donor)
def create_donor(donor: schemas.DonorCreate, db: Session = Depends(get_db)):
    db_donor = models.Donor(
        name=donor.name,
        email=donor.email,
        phone=donor.phone,
        amount=donor.amount,
        blessing_content=donor.blessing_content,
    )
    db.add(db_donor)
    db.commit()
    db.refresh(db_donor)
    return db_donor


@router.get("/", response_model=List[schemas.Donor])
def get_donors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    donors = db.query(models.Donor).offset(skip).limit(limit).all()
    return donors


@router.get("/{donor_id}", response_model=schemas.Donor)
def get_donor(donor_id: int, db: Session = Depends(get_db)):
    donor = db.query(models.Donor).filter(models.Donor.id == donor_id).first()
    if not donor:
        raise HTTPException(status_code=404, detail="功德主不存在")
    return donor
