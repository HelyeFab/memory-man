"""Project detection utilities."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List


def detect_project_info(cwd: Optional[str] = None) -> Dict[str, str]:
    """Auto-detect project information from current directory."""
    if cwd is None:
        cwd = os.getcwd()
    
    path = Path(cwd)
    project_info = {
        "name": path.name,
        "type": "unknown",
        "language": "unknown",
        "framework": "unknown",
        "description": ""
    }
    
    # Check for common project files
    files = list(path.glob("*"))
    file_names = [f.name for f in files]
    
    # Python projects
    if "pyproject.toml" in file_names or "setup.py" in file_names or "requirements.txt" in file_names:
        project_info["type"] = "python"
        project_info["language"] = "python"
        
        # Check for frameworks
        if "manage.py" in file_names:
            project_info["framework"] = "django"
        elif "app.py" in file_names or "main.py" in file_names:
            project_info["framework"] = "flask/fastapi"
        elif "pyproject.toml" in file_names:
            # Check pyproject.toml for more info
            try:
                with open(path / "pyproject.toml", "r") as f:
                    content = f.read()
                    if "fastapi" in content.lower():
                        project_info["framework"] = "fastapi"
                    elif "flask" in content.lower():
                        project_info["framework"] = "flask"
                    elif "django" in content.lower():
                        project_info["framework"] = "django"
            except Exception:
                pass
    
    # JavaScript/TypeScript projects
    elif "package.json" in file_names:
        project_info["type"] = "javascript"
        project_info["language"] = "javascript"
        
        # Check package.json for more info
        try:
            with open(path / "package.json", "r") as f:
                pkg_data = json.load(f)
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                
                if "typescript" in deps:
                    project_info["language"] = "typescript"
                if "react" in deps:
                    project_info["framework"] = "react"
                elif "vue" in deps:
                    project_info["framework"] = "vue"
                elif "angular" in deps:
                    project_info["framework"] = "angular"
                elif "next" in deps:
                    project_info["framework"] = "nextjs"
                elif "express" in deps:
                    project_info["framework"] = "express"
                
                if "description" in pkg_data:
                    project_info["description"] = pkg_data["description"]
        except Exception:
            pass
    
    # Rust projects
    elif "Cargo.toml" in file_names:
        project_info["type"] = "rust"
        project_info["language"] = "rust"
        project_info["framework"] = "cargo"
    
    # Go projects
    elif "go.mod" in file_names:
        project_info["type"] = "go"
        project_info["language"] = "go"
        project_info["framework"] = "go"
    
    # Java projects
    elif "pom.xml" in file_names:
        project_info["type"] = "java"
        project_info["language"] = "java"
        project_info["framework"] = "maven"
    elif "build.gradle" in file_names:
        project_info["type"] = "java"
        project_info["language"] = "java"
        project_info["framework"] = "gradle"
    
    # Check for git repository
    if (path / ".git").exists():
        project_info["git"] = "true"
        
        # Try to get git remote info
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=path
            )
            if result.returncode == 0:
                project_info["git_remote"] = result.stdout.strip()
        except Exception:
            pass
    
    return project_info


def get_project_context(cwd: Optional[str] = None) -> Dict[str, str]:
    """Get relevant project context for memory storage."""
    project_info = detect_project_info(cwd)
    
    context = {
        "project_type": project_info["type"],
        "language": project_info["language"],
        "framework": project_info["framework"],
        "working_directory": cwd or os.getcwd(),
    }
    
    if project_info.get("git_remote"):
        context["git_remote"] = project_info["git_remote"]
    
    return context


def suggest_memory_category(content: str, project_info: Dict[str, str]) -> str:
    """Suggest appropriate memory category based on content and project."""
    content_lower = content.lower()
    
    # Architecture keywords
    if any(word in content_lower for word in ["architecture", "design", "pattern", "structure", "database", "api"]):
        return "architecture"
    
    # Setup keywords
    if any(word in content_lower for word in ["install", "setup", "config", "environment", "deploy"]):
        return "setup"
    
    # Bug fix keywords
    if any(word in content_lower for word in ["bug", "fix", "error", "issue", "problem", "solution"]):
        return "bug_fix"
    
    # Command keywords
    if any(word in content_lower for word in ["command", "run", "script", "npm", "pip", "cargo"]):
        return "command"
    
    # TODO keywords
    if any(word in content_lower for word in ["todo", "future", "plan", "next", "implement"]):
        return "todo"
    
    # Pattern keywords
    if any(word in content_lower for word in ["pattern", "utility", "helper", "function", "class"]):
        return "pattern"
    
    # Default based on project type
    if project_info["type"] == "python":
        return "pattern"
    elif project_info["type"] == "javascript":
        return "pattern"
    else:
        return "general"


def extract_tags_from_content(content: str, project_info: Dict[str, str]) -> List[str]:
    """Extract relevant tags from content and project context."""
    tags = []
    content_lower = content.lower()
    
    # Add project-specific tags
    if project_info["language"] != "unknown":
        tags.append(project_info["language"])
    
    if project_info["framework"] != "unknown":
        tags.append(project_info["framework"])
    
    # Technology tags
    tech_keywords = {
        "database": ["postgres", "mysql", "sqlite", "redis", "mongodb"],
        "web": ["html", "css", "javascript", "react", "vue", "angular"],
        "auth": ["jwt", "oauth", "authentication", "authorization", "session"],
        "api": ["rest", "graphql", "api", "endpoint", "route"],
        "testing": ["test", "unit", "integration", "mock", "jest", "pytest"],
        "deployment": ["docker", "kubernetes", "aws", "azure", "heroku"],
        "tools": ["git", "github", "gitlab", "ci/cd", "pipeline"]
    }
    
    for category, keywords in tech_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            tags.append(category)
            # Add specific keywords found
            for keyword in keywords:
                if keyword in content_lower:
                    tags.append(keyword)
    
    # Remove duplicates and return
    return list(set(tags))