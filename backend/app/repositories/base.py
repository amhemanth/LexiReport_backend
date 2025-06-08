from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException, status
from app.db.base_class import Base
from app.core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with default CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """
        Initialize repository with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get object by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {str(e)}")
            raise DatabaseError(f"Error retrieving {self.model.__name__}")

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None
    ) -> List[ModelType]:
        """
        Get multiple objects with filtering and ordering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field-value pairs to filter by
            order_by: Dictionary of field-direction pairs to order by
        """
        try:
            query = db.query(self.model)
            
            # Apply filters
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model, field).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model, field) == value)
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            # Apply ordering
            if order_by:
                for field, direction in order_by.items():
                    if hasattr(self.model, field):
                        if direction.lower() == 'desc':
                            query = query.order_by(desc(getattr(self.model, field)))
                        else:
                            query = query.order_by(asc(getattr(self.model, field)))
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            raise DatabaseError(f"Error retrieving {self.model.__name__} list")

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create new object."""
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise DatabaseError(f"Error creating {self.model.__name__}")

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update object."""
        try:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise DatabaseError(f"Error updating {self.model.__name__}")

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Remove object."""
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {str(e)}")
            raise DatabaseError(f"Error deleting {self.model.__name__}")

    def count(
        self, db: Session, *, filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count objects with optional filtering.
        
        Args:
            db: Database session
            filters: Dictionary of field-value pairs to filter by
        """
        try:
            query = db.query(self.model)
            
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model, field).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model, field) == value)
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise DatabaseError(f"Error counting {self.model.__name__}")

    def exists(self, db: Session, *, id: Any) -> bool:
        """Check if object exists by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {id}: {str(e)}")
            raise DatabaseError(f"Error checking existence of {self.model.__name__}")

    def get_by_field(
        self, db: Session, *, field: str, value: Any
    ) -> Optional[ModelType]:
        """
        Get object by field value.
        
        Args:
            db: Database session
            field: Field name to filter by
            value: Value to filter by
        """
        try:
            if hasattr(self.model, field):
                return db.query(self.model).filter(getattr(self.model, field) == value).first()
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by {field}={value}: {str(e)}")
            raise DatabaseError(f"Error retrieving {self.model.__name__}")

    def get_multi_by_field(
        self, db: Session, *, field: str, value: Any,
        skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple objects by field value.
        
        Args:
            db: Database session
            field: Field name to filter by
            value: Value to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
        """
        try:
            if hasattr(self.model, field):
                return db.query(self.model).filter(
                    getattr(self.model, field) == value
                ).offset(skip).limit(limit).all()
            return []
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by {field}={value}: {str(e)}")
            raise DatabaseError(f"Error retrieving {self.model.__name__} list") 