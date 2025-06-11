# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyGithub",
#   "jinja2",
#   "python-dotenv",
#   "rich>=13.0.0"
# ]
# ///

"""Script para actualizar automáticamente el README público del perfil de la organización."""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from github import Github
from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console

# Definición de tipos específicos
type RepoInfo = dict[str, str | int]
type OrgInfo = dict[str, str | int]
type MemberInfo = dict[str, str]
type UpdateInfo = dict[str, str]
type CommonResource = dict[str, str]

console = Console()

def create_readme(path: Path | None = None ,**kwargs:str) -> str:
    """Crea el README.md base para un repositorio usando el template Jinja2."""

    if path is None:
        path = Path.cwd()
    name: str | None = kwargs.get("name", "NoName")
    year = kwargs.get("year", datetime.now().year)
    # Get the directory where the script is located
    script_dir: Path = Path(__file__).parent
    template_dir: Path = script_dir / "templates"

    # Load Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir))
    template: Template = env.get_template("profile_readme.md.jinja2")


    # Render template with provided data
    readme_content = template.render(
        name=name,
        current_year=year
    )
    return readme_content


def get_organization_data(org_name: str, token: str) -> dict[str, Any]:
    """Obtiene información de la organización de GitHub."""
    try:
        g = Github(token)
        org = g.get_organization(org_name)

        # Obtener repositorios públicos
        repos = []
        for repo in org.get_repos(type="public"):
            if not repo.fork:  # Excluir forks
                repo_info: RepoInfo = {
                    "name": repo.name,
                    "description": repo.description or "Sin descripción",
                    "html_url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language or "N/A",
                    "updated_at": repo.updated_at.strftime("%Y-%m-%d") if repo.updated_at else "N/A"
                }
                repos.append(repo_info)

        # Ordenar por estrellas
        repos.sort(key=lambda x: x["stars"], reverse=True)

        # Obtener información básica de la organización
        org_info: OrgInfo = {
            "name": org.name,
            "login": org.login,
            "description": org.description or "Sin descripción",
            "html_url": org.html_url,
            "public_repos": org.public_repos,
            "followers": org.followers,
            "location": org.location or "No especificada",
            "blog": org.blog or "",
            "email": org.email or "",
            "created_at": org.created_at.strftime("%Y-%m-%d") if org.created_at else "N/A"
        }

        # Obtener algunos miembros públicos (limitado a los primeros 10)
        members = []
        try:
            for member in org.get_public_members()[:10]:
                member_info: MemberInfo = {
                    "login": member.login,
                    "html_url": member.html_url,
                    "avatar_url": member.avatar_url
                }
                members.append(member_info)
        except Exception as e:
            console.print(f"[yellow]No se pudieron obtener los miembros: {e}[/yellow]")

        return {
            "organization": org_info,
            "repositories": repos[:10],  # Limitar a los 10 primeros
            "members": members,
            "total_repos": len(repos)
        }

    except Exception as e:
        console.print(f"[red]Error al obtener datos de GitHub: {e}[/red]")
        return {
            "organization": {"name": org_name, "description": "Organización no encontrada"},
            "repositories": [],
            "members": [],
            "total_repos": 0
        }


def load_github_token() -> str:
    """Carga el token de GitHub desde las variables de entorno de GitHub Actions."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "No se encontró el token de GitHub (GITHUB_TOKEN) en las variables de entorno"
        )
    return token


def write_stream(content: str, path: Path) -> None:
    """Escribe el contenido en un archivo, creando directorios si es necesario."""
    path.parent.mkdir(parents=True, exist_ok=True)  # Asegura que el directorio exista
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


    # Write to profile/README.md instead of the provided path




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

    # Generar README del perfil - usar la función refactorizada
    nueva_portada: str = create_readme(
        name="Alumnithon",
    )
    print("Generando README del perfil de la organización...")
    write_stream(nueva_portada, Path("profile/README.md"))
    print("README del perfil de la organización generado correctamente.")

if __name__ == "__main__":
    main()