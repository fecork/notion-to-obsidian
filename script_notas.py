from __future__ import annotations

import pandas as pd
from pathlib import Path
import re
from collections import Counter

# Ajusta esto al nombre real de tu archivo CSV
CSV_PATH = Path(
    "ExportBlock-741f5d32-6852-42dd-8e67-3d0a65092959-Part-1/"
    "Ideas 27dfebb57bdd8021907ac30f184566b9_all.csv"
)
OUTPUT_DIR = Path("obsidian_ideas")


def slugify(text: str, max_len: int = 60) -> str:
    """Create a filesystem-safe slug from a text."""
    text = re.sub(r"\s+", " ", str(text)).strip()
    text = text.replace("\n", " ")
    text = text[:max_len]
    text = re.sub(r"[^\w\- ]", "", text)
    text = text.strip().replace(" ", "-")
    return text or "note"


def clean_str(value) -> str | None:
    """Normalize string cells; return None if empty/null."""
    if isinstance(value, str):
        v = value.strip()
        return v if v else None
    return None


def split_tags(cell) -> list[str]:
    """Split tags by comma/semicolon."""
    if isinstance(cell, str):
        return [t.strip() for t in re.split(r"[;,]", cell) if t.strip()]
    return []


def extract_links(connections_cell) -> list[str]:
    """
    80/20: Si en '🔗 Conexiones' hay textos tipo:
    - Conectar con "Métricas robustas"
    Los convertimos en [[Métricas robustas]] para el grafo.
    Si no hay comillas, guardamos el texto como está.
    """
    if not isinstance(connections_cell, str):
        return []

    text = connections_cell.strip()
    if not text:
        return []

    links = []
    # Cosas entre "" o "" -> wikilinks
    candidates = re.findall(r"[\"\"](.*?)[\"\"]", text)
    for c in candidates:
        c = c.strip()
        if c:
            links.append(f"[[{c}]]")

    # Si no encontramos nada citado, usamos el texto completo como referencia
    if not links:
        links.append(text)

    return links


def build_frontmatter(
    row, note_id: str, title: str, tags: list[str], links: list[str]
) -> str:
    """Build minimal YAML frontmatter without dependencias raras."""
    fm = {
        "id": note_id,
        "title": title,
    }

    estado = clean_str(row.get("Estado"))
    tipo_ = clean_str(row.get("💡 Tipo"))
    fuente = clean_str(row.get("📚 Fuente"))

    if estado:
        fm["estado"] = estado
    if tipo_:
        fm["tipo"] = tipo_
    if fuente:
        fm["fuente"] = fuente
    if tags:
        fm["tags"] = tags
    if links:
        fm["links"] = links

    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            safe = str(value).replace('"', '\\"')
            lines.append(f'{key}: "{safe}"')

    lines.append("---")
    return "\n".join(lines)


def print_header(title: str):
    """Imprime un encabezado bonito."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Imprime el título de una sección."""
    print(f"\n▶ {title}")


def print_summary(stats: dict):
    """Imprime un resumen bonito de las estadísticas."""
    print_header("RESUMEN DEL PROCESO")

    print("\n📊 Estadísticas:")
    print(f"   • Total de notas creadas: {stats['total_notes']}")
    print(f"   • Notas con tags: {stats['notes_with_tags']}")
    print(f"   • Notas con conexiones: {stats['notes_with_links']}")
    print(f"   • Total de tags únicos: {stats['unique_tags']}")
    print(f"   • Total de conexiones: {stats['total_links']}")

    if stats["estados"]:
        print("\n📋 Distribución por estado:")
        for estado, count in stats["estados"].most_common():
            print(f"   • {estado}: {count}")

    if stats["tipos"]:
        print("\n💡 Distribución por tipo:")
        for tipo, count in stats["tipos"].most_common():
            print(f"   • {tipo}: {count}")

    print("\n📁 Ubicación:")
    print(f"   {stats['output_path']}")

    print("\n" + "=" * 60)
    print("✓ Proceso completado exitosamente!")
    print("=" * 60 + "\n")


def main():
    print_header("CONVERSIÓN CSV → MARKDOWN PARA OBSIDIAN")

    print_section("Leyendo archivo CSV")
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"   ✓ CSV leído: {CSV_PATH.name}")
        print(f"   ✓ Filas encontradas: {len(df)}")
    except FileNotFoundError:
        print(f"   ✗ Error: No se encontró el archivo {CSV_PATH}")
        return
    except Exception as e:
        print(f"   ✗ Error leyendo CSV: {e}")
        return

    print_section("Creando carpeta de salida")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Carpeta creada/verificada: {OUTPUT_DIR}")

    print_section("Procesando filas y generando notas")

    # Estadísticas
    stats = {
        "total_notes": 0,
        "notes_with_tags": 0,
        "notes_with_links": 0,
        "unique_tags": set(),
        "total_links": 0,
        "estados": Counter(),
        "tipos": Counter(),
        "output_path": OUTPUT_DIR.resolve(),
    }

    for idx, row in df.iterrows():
        idea = clean_str(row.get("📝 Idea")) or f"Idea {idx + 1}"
        note_id = f"idea-{idx + 1:03d}"
        slug = slugify(idea)
        title = idea

        tags = split_tags(row.get("🏷️ Tags"))
        links = extract_links(row.get("🔗 Conexiones"))

        frontmatter = build_frontmatter(row, note_id, title, tags, links)

        body_parts = [
            frontmatter,
            "",
            "## Idea",
            idea,
        ]

        conexiones_raw = clean_str(row.get("🔗 Conexiones"))
        if conexiones_raw:
            body_parts += [
                "",
                "## Conexiones (texto original)",
                conexiones_raw,
            ]

        content = "\n".join(body_parts)
        file_path = OUTPUT_DIR / f"{note_id}-{slug}.md"
        file_path.write_text(content, encoding="utf-8")

        # Actualizar estadísticas
        stats["total_notes"] += 1
        if tags:
            stats["notes_with_tags"] += 1
            stats["unique_tags"].update(tags)
        if links:
            stats["notes_with_links"] += 1
            stats["total_links"] += len(links)

        estado = clean_str(row.get("Estado"))
        if estado:
            stats["estados"][estado] += 1

        tipo = clean_str(row.get("💡 Tipo"))
        if tipo:
            stats["tipos"][tipo] += 1

    # Convertir set a número
    stats["unique_tags"] = len(stats["unique_tags"])

    print(f"   ✓ {stats['total_notes']} archivos markdown generados")

    print_summary(stats)


if __name__ == "__main__":
    main()
