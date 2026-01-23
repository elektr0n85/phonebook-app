"""
Base CRUD class with generic database operations.
"""
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

# Type variables for generic CRUD
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with default methods for Create, Read, Update, Delete.
    
    Generic types:
        - ModelType: SQLAlchemy model
        - CreateSchemaType: Pydantic schema for creation
        - UpdateSchemaType: Pydantic schema for update
        
    Usage:
        class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
            pass
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance or None if not found
            
        Security: Returns None instead of raising exception (prevent info leakage)
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[ModelType]:
        """
        Get multiple records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
            
        Security: Limit is capped at 100 to prevent resource exhaustion
        """
        # Cap limit at 100
        limit = min(limit, 100)
        
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
            
        Returns:
            Created model instance
            
        Security: Validation already done by Pydantic schema
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.
        
        Args:
            db: Database session
            db_obj: Existing model instance from database
            obj_in: Pydantic schema or dict with update data
            
        Returns:
            Updated model instance
            
        Security: 
            - Only updates fields present in obj_in (partial update)
            - Validation already done by Pydantic schema
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, *, id: int) -> ModelType | None:
        """
        Delete a record by ID.
        
        Args:
            db: Database session
            id: Record ID to delete
            
        Returns:
            Deleted model instance or None if not found
            
        Security: Hard delete (permanent removal from database)
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
