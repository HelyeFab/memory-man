#!/usr/bin/env python3
"""Display memory statistics."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory_man.database import get_db
from memory_man.models.memory import Memory
from sqlalchemy import func, select
from rich.console import Console
from rich.table import Table


async def show_stats():
    """Show memory statistics."""
    console = Console()
    
    async with get_db() as db:
        # Total memories
        stmt = select(func.count(Memory.id))
        result = await db.execute(stmt)
        total_memories = result.scalar()
        
        # By project
        stmt = select(
            Memory.project_name,
            func.count(Memory.id).label("count")
        ).group_by(Memory.project_name).order_by(func.count(Memory.id).desc())
        result = await db.execute(stmt)
        projects = result.all()
        
        # By category
        stmt = select(
            Memory.category,
            func.count(Memory.id).label("count")
        ).group_by(Memory.category).order_by(func.count(Memory.id).desc())
        result = await db.execute(stmt)
        categories = result.all()
        
        # By importance
        stmt = select(
            Memory.importance,
            func.count(Memory.id).label("count")
        ).group_by(Memory.importance).order_by(Memory.importance.desc())
        result = await db.execute(stmt)
        importance_levels = result.all()
        
        # Display results
        console.print(f"\n[bold blue]🧠 Memory-Man Statistics[/bold blue]")
        console.print(f"Total memories: [bold]{total_memories}[/bold]\n")
        
        # Projects table
        if projects:
            projects_table = Table(title="Memories by Project")
            projects_table.add_column("Project", style="cyan")
            projects_table.add_column("Count", style="magenta")
            
            for project, count in projects:
                projects_table.add_row(project, str(count))
            
            console.print(projects_table)
        
        # Categories table
        if categories:
            categories_table = Table(title="Memories by Category")
            categories_table.add_column("Category", style="green")
            categories_table.add_column("Count", style="magenta")
            
            for category, count in categories:
                categories_table.add_row(category, str(count))
            
            console.print(categories_table)
        
        # Importance table
        if importance_levels:
            importance_table = Table(title="Memories by Importance")
            importance_table.add_column("Importance", style="yellow")
            importance_table.add_column("Count", style="magenta")
            
            for importance, count in importance_levels:
                importance_table.add_row(str(importance), str(count))
            
            console.print(importance_table)


if __name__ == "__main__":
    asyncio.run(show_stats())