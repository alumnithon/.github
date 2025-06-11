#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyGithub",
#   "jinja2",
#   "python-dotenv",
#   "rich>=13.0.0"
# ]
# ///

"""
Script para actualizar automáticamente el README del perfil de la organización y mantener
la estructura de los repositorios de los equipos.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from github import Github, Repository
    from github.Organization import Organization
    from jinja2 import Environment, FileSystemLoader
    from rich.console import Console
except ImportError as e:
    raise ImportError(
        "Asegúrate de tener instaladas las dependencias necesarias. "
        "Ejecuta: pip install -r requirements.txt"
    ) from e
# Definición de tipos específicos
type RepoInfo  = dict[str, str]
type YearSubjects = dict[str, list[dict[str, Any]]]
type UpdateInfo = dict[str, str]
type CommonResource = dict[str, str]

console = Console()


def load_github_token() -> str:
    """Carga el token de GitHub desde las variables de entorno de GitHub Actions."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "No se encontró el token de GitHub (GITHUB_TOKEN) en las variables de entorno"
        )
    return token



def create_readme(path: Path, name: str, description: str) -> None:
    """Crea el README.md base para un repositorio."""
    current_year = datetime.now().year
    template = """# 📚 {name}

## 📝 Descripción
{description}

## 📂 Estructura del Repositorio

- 📁 **notes/**: Apuntes de clase organizados por año
  - 📚 **teoria/**: Contenido teórico por temas
  - 💻 **practica/**: Ejercicios y trabajos prácticos
- 📁 **examples/**: Ejemplos prácticos y código
  - 📚 **teoria/**: Ejemplos de conceptos teóricos
  - 💻 **practica/**: Ejemplos de implementación práctica
- 📖 **study-guides/**: Guías de estudio y material de práctica
  - 📚 **teoria/**: Guías de estudio teóricas
  - 💻 **practica/**: Guías de ejercicios prácticos
- 📁 **resources/**: Recursos adicionales y material de referencia
  - 📚 **teoria/**: Recursos para contenido teórico
  - 💻 **practica/**: Recursos para trabajos prácticos

## 🗓️ Contenido Actual ({year})

### 📚 Temas Teóricos
- [Por definir]

### 💻 Temas Prácticos
- [Por definir]

### 📖 Guías de Estudio
- [Por agregar]

### 💻 Ejemplos
- [Por agregar]

## 🤝 Contribuir
¡Las contribuciones son bienvenidas! Por favor, lee nuestras guías de contribución.

## 📜 Licencia
Este repositorio está bajo la Licencia MIT.
"""
    path.write_text(
        template.format(name=name, description=description, year=current_year),
        encoding="utf-8",
    )


def has_changes(repo_path: Path) -> bool:
    """Verifica si hay cambios en el repositorio."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())

def main():
    """Función principal para actualizar el README del perfil de la organización."""
    token = load_github_token()
    g = Github(token)
    org: Organization = g.get_organization("alumnithon")  # Cambia por tu organización

    # Cargar plantilla Jinja2
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("profile_readme_template.md")

    # Obtener información de los repositorios
    repos: list[Repository] = org.get_repos()

    for repo in track(repos, description="Actualizando repositorios..."):
        try:
            init_repo_structure(repo)
        except Exception as e:
            console.print(f"[red]Error al actualizar {repo.name}: {e}[/red]")

    # Generar README del perfil
    readme_content = template.render(repositories=repos)
    (Path.home() / "profile_readme.md").write_text(readme_content, encoding="utf-8")
    console.print("[green]README del perfil actualizado exitosamente.[/green]")


if __name__ == "__main__":
    main()