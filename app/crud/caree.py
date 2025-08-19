from sqlalchemy.orm import Session
from models.caree import Caree
from models.user_relationship import UserRelationship, RelationshipType
from schema.caree import CareeCreateRequest


def create_caree(db: Session, caree_data: CareeCreateRequest, creator_user_id: str) -> Caree:
    caree = Caree(
        name=caree_data.name,
        gender=caree_data.gender,
        birth_date=caree_data.birth_date,
        created_by_user_id=creator_user_id
    )
    db.add(caree)
    db.commit()
    db.refresh(caree)
    
    relationship = UserRelationship(
        protector_user_id=creator_user_id,
        caree_id=caree.caree_id,
        relationship_type=RelationshipType.primary
    )
    db.add(relationship)
    db.commit()
    
    return caree


def get_caree_by_id(db: Session, caree_id: int) -> Caree:
    return db.query(Caree).filter(Caree.caree_id == caree_id).first()


def get_carees_by_user(db: Session, user_id: str) -> list[Caree]:
    return db.query(Caree).filter(Caree.created_by_user_id == user_id).all()


def delete_caree_by_user(db: Session, user_id: str) -> bool:
    caree = db.query(Caree).filter(Caree.created_by_user_id == user_id).first()
    if caree:
        from models.registration_code import RegistrationCode
        from models.user_relationship import UserRelationship
        from models.safe_zone import SafeZone
        from models.care_settings import CareSettings
        from models.position_history import PositionHistory
        from models.alert_history import AlertHistory
        
        db.query(RegistrationCode).filter(RegistrationCode.caree_id == caree.caree_id).delete()
        db.query(UserRelationship).filter(UserRelationship.caree_id == caree.caree_id).delete()
        db.query(SafeZone).filter(SafeZone.caree_id == caree.caree_id).delete()
        db.query(CareSettings).filter(CareSettings.caree_id == caree.caree_id).delete()
        db.query(PositionHistory).filter(PositionHistory.caree_id == caree.caree_id).delete()
        db.query(AlertHistory).filter(AlertHistory.caree_id == caree.caree_id).delete()
        
        db.delete(caree)
        db.commit()
        return True
    return False