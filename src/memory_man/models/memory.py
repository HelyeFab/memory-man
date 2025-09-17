"""Memory database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Memory(Base):
    """Represents a single memory entry."""
    
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    project_name = Column(String(255), nullable=False, default="default")
    category = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=list)  # List of tags
    importance = Column(Integer, default=5)  # 1-10 scale
    context = Column(JSON, default=dict)  # Additional context
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)
    
    # Lifecycle management
    is_archived = Column(Integer, default=0)  # 0=active, 1=archived
    archived_at = Column(DateTime, nullable=True)
    archived_reason = Column(String(255), nullable=True)
    
    # Search optimization
    search_text = Column(Text)  # Concatenated searchable content
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_project_category", "project_name", "category"),
        Index("idx_created_at", "created_at"),
        Index("idx_importance", "importance"),
        Index("idx_archived", "is_archived"),
        Index("idx_project_archived", "project_name", "is_archived"),
    )
    
    def to_dict(self) -> dict:
        """Convert memory to dictionary."""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "category": self.category,
            "content": self.content,
            "tags": self.tags or [],
            "importance": self.importance,
            "context": self.context or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "access_count": self.access_count,
            "is_archived": bool(self.is_archived),
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "archived_reason": self.archived_reason,
        }