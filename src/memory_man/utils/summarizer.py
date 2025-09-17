"""Memory summarization utilities."""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..models.memory import Memory


class MemorySummarizer:
    """Intelligent memory summarization."""
    
    def __init__(self):
        self.max_summary_length = 500
        self.min_memories_to_summarize = 5
        self.days_threshold = 30  # Summarize memories older than 30 days
    
    def should_summarize_project(self, memories: List[Memory]) -> bool:
        """Determine if a project's memories should be summarized."""
        if len(memories) < self.min_memories_to_summarize:
            return False
        
        # Check if there are old memories
        cutoff_date = datetime.utcnow() - timedelta(days=self.days_threshold)
        old_memories = [m for m in memories if m.created_at < cutoff_date]
        
        return len(old_memories) >= self.min_memories_to_summarize
    
    def group_memories_by_category(self, memories: List[Memory]) -> Dict[str, List[Memory]]:
        """Group memories by category."""
        groups = {}
        for memory in memories:
            category = memory.category
            if category not in groups:
                groups[category] = []
            groups[category].append(memory)
        return groups
    
    def extract_key_points(self, content: str) -> List[str]:
        """Extract key points from memory content."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences based on key indicators
        scored_sentences = []
        for sentence in sentences:
            score = self._score_sentence(sentence)
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_sentences[:3]]  # Top 3 sentences
    
    def _score_sentence(self, sentence: str) -> int:
        """Score a sentence for importance."""
        sentence_lower = sentence.lower()
        score = 0
        
        # Technical keywords
        tech_keywords = [
            'api', 'database', 'authentication', 'authorization', 'jwt', 'oauth',
            'redis', 'postgres', 'mysql', 'mongodb', 'docker', 'kubernetes',
            'react', 'angular', 'vue', 'python', 'javascript', 'typescript',
            'fastapi', 'django', 'flask', 'express', 'nextjs', 'nginx'
        ]
        for keyword in tech_keywords:
            if keyword in sentence_lower:
                score += 2
        
        # Decision keywords
        decision_keywords = [
            'decided', 'chose', 'selected', 'implemented', 'because', 'due to',
            'architecture', 'design', 'pattern', 'approach', 'solution'
        ]
        for keyword in decision_keywords:
            if keyword in sentence_lower:
                score += 3
        
        # Problem/solution keywords
        problem_keywords = [
            'fixed', 'solved', 'resolved', 'bug', 'issue', 'problem', 'error',
            'works', 'solution', 'workaround'
        ]
        for keyword in problem_keywords:
            if keyword in sentence_lower:
                score += 2
        
        # Command/setup keywords
        command_keywords = [
            'run', 'install', 'deploy', 'build', 'test', 'start', 'setup',
            'configure', 'command', 'script'
        ]
        for keyword in command_keywords:
            if keyword in sentence_lower:
                score += 1
        
        return score
    
    def summarize_category(self, memories: List[Memory], category: str) -> str:
        """Summarize memories within a category."""
        if not memories:
            return ""
        
        # Sort by importance and recency
        memories.sort(key=lambda m: (m.importance, m.created_at), reverse=True)
        
        # Extract key points from all memories
        all_points = []
        for memory in memories:
            points = self.extract_key_points(memory.content)
            all_points.extend(points)
        
        # Remove duplicates while preserving order
        unique_points = []
        seen = set()
        for point in all_points:
            point_normalized = point.lower().strip()
            if point_normalized not in seen and len(point_normalized) > 10:
                unique_points.append(point)
                seen.add(point_normalized)
        
        # Create summary
        summary_parts = []
        
        # Category header
        summary_parts.append(f"**{category.title()} Summary** ({len(memories)} memories):")
        
        # Key points
        for i, point in enumerate(unique_points[:5], 1):  # Top 5 points
            summary_parts.append(f"{i}. {point}")
        
        # Most important memory
        if memories:
            top_memory = memories[0]
            if top_memory.importance >= 8:
                summary_parts.append(f"\n**Key Decision**: {top_memory.content[:100]}...")
        
        return "\n".join(summary_parts)
    
    def create_project_summary(self, memories: List[Memory], project_name: str) -> str:
        """Create a comprehensive project summary."""
        if not memories:
            return f"No memories found for project: {project_name}"
        
        # Group by category
        categories = self.group_memories_by_category(memories)
        
        # Create summary sections
        summary_parts = []
        summary_parts.append(f"# Project Summary: {project_name}")
        summary_parts.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"Total memories: {len(memories)}")
        summary_parts.append("")
        
        # Prioritize categories
        category_priority = {
            'architecture': 1,
            'setup': 2,
            'bug_fix': 3,
            'pattern': 4,
            'command': 5,
            'todo': 6
        }
        
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: category_priority.get(x[0], 99)
        )
        
        # Generate category summaries
        for category, cat_memories in sorted_categories:
            if cat_memories:
                cat_summary = self.summarize_category(cat_memories, category)
                if cat_summary:
                    summary_parts.append(cat_summary)
                    summary_parts.append("")
        
        # Add recent highlights
        recent_memories = sorted(memories, key=lambda m: m.created_at, reverse=True)[:3]
        if recent_memories:
            summary_parts.append("## Recent Highlights:")
            for memory in recent_memories:
                summary_parts.append(f"- {memory.content[:80]}... (importance: {memory.importance})")
            summary_parts.append("")
        
        # Add most accessed
        popular_memories = sorted(memories, key=lambda m: m.access_count, reverse=True)[:3]
        if popular_memories and popular_memories[0].access_count > 1:
            summary_parts.append("## Most Referenced:")
            for memory in popular_memories:
                summary_parts.append(f"- {memory.content[:80]}... (accessed {memory.access_count} times)")
        
        return "\n".join(summary_parts)
    
    def suggest_archival_candidates(self, memories: List[Memory]) -> List[Tuple[Memory, str]]:
        """Suggest memories that could be archived."""
        candidates = []
        cutoff_date = datetime.utcnow() - timedelta(days=90)  # 3 months old
        
        for memory in memories:
            reasons = []
            
            # Old and low importance
            if memory.created_at < cutoff_date and memory.importance <= 3:
                reasons.append("old and low importance")
            
            # Never accessed and old
            if memory.access_count == 0 and memory.created_at < cutoff_date:
                reasons.append("never accessed")
            
            # Duplicate content detection (simple)
            if len(memory.content) < 20:
                reasons.append("very short content")
            
            # TODO items that are very old
            if (memory.category == "todo" and 
                memory.created_at < datetime.utcnow() - timedelta(days=180)):
                reasons.append("old todo item")
            
            if reasons:
                candidates.append((memory, "; ".join(reasons)))
        
        return candidates
    
    def optimize_memory_storage(self, memories: List[Memory]) -> Dict[str, any]:
        """Analyze memory storage and suggest optimizations."""
        total_memories = len(memories)
        if total_memories == 0:
            return {"total": 0, "suggestions": []}
        
        # Analyze by category
        categories = self.group_memories_by_category(memories)
        category_stats = {}
        for cat, cat_memories in categories.items():
            category_stats[cat] = {
                "count": len(cat_memories),
                "avg_importance": sum(m.importance for m in cat_memories) / len(cat_memories),
                "avg_access": sum(m.access_count for m in cat_memories) / len(cat_memories)
            }
        
        # Generate suggestions
        suggestions = []
        
        # Too many low-importance memories
        low_importance = [m for m in memories if m.importance <= 3]
        if len(low_importance) > total_memories * 0.3:
            suggestions.append(f"Consider archiving {len(low_importance)} low-importance memories")
        
        # Unused memories
        unused = [m for m in memories if m.access_count == 0]
        if len(unused) > 10:
            suggestions.append(f"Review {len(unused)} never-accessed memories")
        
        # Category imbalances
        if "todo" in category_stats and category_stats["todo"]["count"] > total_memories * 0.4:
            suggestions.append("High number of TODO items - consider completing or archiving")
        
        # Old memories
        old_cutoff = datetime.utcnow() - timedelta(days=180)
        old_memories = [m for m in memories if m.created_at < old_cutoff]
        if len(old_memories) > 20:
            suggestions.append(f"Consider summarizing {len(old_memories)} memories older than 6 months")
        
        return {
            "total": total_memories,
            "categories": category_stats,
            "archival_candidates": len(self.suggest_archival_candidates(memories)),
            "suggestions": suggestions
        }