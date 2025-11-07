"""
Script para enriquecer archivos Markdown con wikilinks automáticos.

Analiza todos los archivos markdown en la carpeta especificada, identifica las palabras
más frecuentes y las convierte automáticamente en wikilinks [[...]] para crear más
conexiones en el grafo de Obsidian.

Uso:
    1. Primero ejecuta script_notas.py para generar los markdown
    2. Luego ejecuta este script: python enriquecer_conexiones.py
    3. Los archivos se modificarán in-place agregando los wikilinks
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter
import re

# Configuración
INPUT_DIR = Path("obsidian_ideas")
MIN_WORD_LENGTH = 4
MIN_FREQUENCY = 2  # Mínimo de apariciones para considerar una palabra
TOP_N_WORDS = 20  # Top N palabras a convertir en wikilinks

# Stopwords comunes en español e inglés (palabras a ignorar)
STOPWORDS = {
    # Español
    "con",
    "para",
    "por",
    "que",
    "del",
    "los",
    "las",
    "una",
    "uno",
    "este",
    "esta",
    "estos",
    "estas",
    "como",
    "más",
    "muy",
    "también",
    "pero",
    "sin",
    "sobre",
    "entre",
    "hasta",
    "desde",
    "hacia",
    "durante",
    "mediante",
    "puede",
    "pueden",
    "ser",
    "son",
    "tiene",
    "tienen",
    "hacer",
    "hace",
    "hacen",
    "decir",
    "dice",
    "ver",
    "vez",
    "año",
    "años",
    "día",
    "días",
    "caso",
    "casos",
    "parte",
    "partes",
    "forma",
    "formas",
    "manera",
    "maneras",
    "tipo",
    "tipos",
    "todo",
    "todos",
    "todas",
    "cada",
    "cual",
    "cuales",
    "cuando",
    "donde",
    "cualquier",
    "algunos",
    "algunas",
    "otro",
    "otros",
    "otra",
    "otras",
    "mismo",
    "misma",
    "mismos",
    "mismas",
    "solo",
    "sola",
    "solas",
    "tanto",
    "tanta",
    "tantos",
    "tantas",
    "menos",
    "mayor",
    "mayores",
    "menor",
    "menores",
    "mejor",
    "mejores",
    "peor",
    "peores",
    "nuevo",
    "nueva",
    "nuevos",
    "nuevas",
    "gran",
    "grande",
    "grandes",
    "pequeño",
    "pequeña",
    "pequeños",
    "pequeñas",
    # Inglés comunes
    "with",
    "that",
    "this",
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "from",
    "have",
    "has",
    "had",
    "was",
    "were",
    "been",
    "being",
    "are",
    "is",
    "it",
    "its",
    "they",
    "them",
    "their",
    "there",
    "these",
    "those",
    "what",
    "which",
    "who",
    "when",
    "where",
    "why",
    "how",
    "can",
    "could",
    "should",
    "would",
    "will",
    "shall",
    "may",
    "might",
    "must",
    "about",
    "into",
    "onto",
    "upon",
    "within",
    "without",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "under",
    "over",
    "between",
    "among",
    "while",
    "because",
    "although",
    "though",
    "however",
    "therefore",
    "thus",
    "hence",
    "more",
    "most",
    "less",
    "least",
    "other",
    "others",
    "another",
    "such",
    "same",
    "very",
    "much",
    "many",
    "some",
    "any",
    "all",
    "both",
    "each",
    "every",
    "none",
    "not",
    "no",
    "yes",
    "if",
    "then",
    "else",
    "also",
    "too",
    "either",
    "neither",
    "only",
    "just",
    "even",
    "still",
    "yet",
    "already",
    "again",
    "once",
    "twice",
    "here",
    "idea",
    "ideas",  # Palabras específicas del dominio que no son útiles
}


def extract_body_text(content: str) -> str:
    """Extrae el texto del cuerpo, excluyendo el frontmatter YAML."""
    # Dividir por el primer --- que cierra el frontmatter
    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return content.strip()


def normalize_word(word: str) -> str:
    """Normaliza una palabra: lowercase y elimina puntuación."""
    word = word.lower().strip()
    # Eliminar puntuación al final
    word = re.sub(r"[^\w]+$", "", word)
    return word


def extract_words(text: str) -> list[str]:
    """Extrae palabras del texto, normalizadas y filtradas."""
    # Dividir por espacios y puntuación
    words = re.findall(r"\b\w+\b", text.lower())

    filtered = []
    for word in words:
        normalized = normalize_word(word)
        # Filtrar: longitud mínima, no stopword, solo letras
        if (
            len(normalized) >= MIN_WORD_LENGTH
            and normalized not in STOPWORDS
            and normalized.isalpha()
        ):
            filtered.append(normalized)

    return filtered


def find_frequent_words(markdown_files: list[Path]) -> list[tuple[str, int]]:
    """Analiza todos los markdown y encuentra las palabras más frecuentes."""
    all_words = []
    errors = []

    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            body_text = extract_body_text(content)
            words = extract_words(body_text)
            all_words.extend(words)
        except Exception as e:
            errors.append((md_file.name, str(e)))
            continue

    if errors:
        print(f"   ⚠ {len(errors)} archivo(s) con errores (se omitieron)")

    # Contar frecuencias
    word_counts = Counter(all_words)

    # Filtrar por frecuencia mínima y obtener top N
    frequent = [
        (word, count) for word, count in word_counts.items() if count >= MIN_FREQUENCY
    ]
    frequent.sort(key=lambda x: x[1], reverse=True)

    return frequent[:TOP_N_WORDS]


def add_wikilinks_to_text(text: str, words_to_link: list[str]) -> str:
    """
    Agrega wikilinks [[...]] a las palabras frecuentes en el texto.
    Evita crear wikilinks dentro de wikilinks existentes.
    """
    # Patrón para encontrar wikilinks existentes
    existing_wikilink_pattern = r"\[\[[^\]]+\]\]"

    # Dividir el texto en partes: texto normal y wikilinks existentes
    parts = re.split(f"({existing_wikilink_pattern})", text)

    result_parts = []

    for part in parts:
        # Si es un wikilink existente, dejarlo tal cual
        if re.match(existing_wikilink_pattern, part):
            result_parts.append(part)
        else:
            # Procesar el texto normal (ya sabemos que no tiene wikilinks)
            modified_part = part

            # Para cada palabra frecuente, buscar y reemplazar
            # Procesar de mayor a menor longitud para evitar conflictos
            sorted_words = sorted(words_to_link, key=len, reverse=True)

            for word in sorted_words:
                # Patrón: palabra completa como límite de palabra, case-insensitive
                pattern = r"\b" + re.escape(word) + r"\b"

                def replace_func(match):
                    matched_text = match.group(0)
                    start = match.start()
                    end = match.end()
                    # Verificar contexto antes y después para evitar wikilinks dentro de wikilinks
                    before = modified_part[max(0, start - 2) : start]
                    after = modified_part[end : min(len(modified_part), end + 2)]
                    # Si hay '[[' antes o ']]' después, no modificar
                    if "[[" in before or "]]" in after:
                        return matched_text
                    return f"[[{matched_text}]]"

                modified_part = re.sub(
                    pattern, replace_func, modified_part, flags=re.IGNORECASE
                )

            result_parts.append(modified_part)

    return "".join(result_parts)


def process_markdown_file(md_file: Path, words_to_link: list[str]) -> bool:
    """Procesa un archivo markdown agregando wikilinks. Retorna True si se modificó."""
    try:
        content = md_file.read_text(encoding="utf-8")

        # Separar frontmatter y cuerpo
        parts = content.split("---", 2)
        if len(parts) < 3:
            # No tiene frontmatter estándar, procesar todo
            new_body = add_wikilinks_to_text(content, words_to_link)
            if new_body != content:
                md_file.write_text(new_body, encoding="utf-8")
                return True
            return False

        frontmatter = parts[0] + "---" + parts[1] + "---"
        body = parts[2]

        # Procesar solo el cuerpo
        new_body = add_wikilinks_to_text(body, words_to_link)

        if new_body != body:
            new_content = frontmatter + "\n" + new_body
            md_file.write_text(new_content, encoding="utf-8")
            return True

        return False
    except Exception as e:
        print(f"Error procesando {md_file.name}: {e}")
        return False


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

    print(f"\n📊 Estadísticas:")
    print(f"   • Archivos analizados: {stats['total_files']}")
    print(f"   • Archivos modificados: {stats['modified_files']}")
    print(f"   • Archivos sin cambios: {stats['unchanged_files']}")
    print(f"   • Palabras convertidas en wikilinks: {stats['words_linked']}")

    if stats["top_words"]:
        print(f"\n🔗 Top {min(10, len(stats['top_words']))} palabras más frecuentes:")
        for i, (word, count) in enumerate(stats["top_words"][:10], 1):
            print(f"   {i:2d}. {word:20s} → {count:3d} apariciones")

    print(f"\n⚙️  Configuración aplicada:")
    print(f"   • Longitud mínima de palabra: {stats['min_length']}")
    print(f"   • Frecuencia mínima: {stats['min_freq']}")
    print(f"   • Top N palabras: {stats['top_n']}")

    print("\n" + "=" * 60)
    print("✓ Proceso completado exitosamente!")
    print("=" * 60 + "\n")


def main():
    """Función principal."""
    print_header("ENRIQUECIMIENTO DE CONEXIONES CON WIKILINKS")

    print_section("Verificando carpeta de entrada")
    if not INPUT_DIR.exists():
        print(f"   ✗ Error: La carpeta {INPUT_DIR} no existe.")
        print(f"   → Ejecuta primero script_notas.py para generar los markdown.")
        return

    print(f"   ✓ Carpeta encontrada: {INPUT_DIR}")

    print_section("Buscando archivos markdown")
    markdown_files = list(INPUT_DIR.glob("*.md"))

    if not markdown_files:
        print(f"   ✗ No se encontraron archivos .md en {INPUT_DIR}")
        return

    print(f"   ✓ {len(markdown_files)} archivos markdown encontrados")

    print_section("Analizando contenido y extrayendo palabras frecuentes")
    print(f"   → Procesando archivos...")

    frequent_words = find_frequent_words(markdown_files)

    if not frequent_words:
        print(f"   ✗ No se encontraron palabras frecuentes para enlazar.")
        print(f"   → Ajusta MIN_FREQUENCY o MIN_WORD_LENGTH si es necesario.")
        return

    words_to_link = [word for word, count in frequent_words]

    print(f"   ✓ {len(frequent_words)} palabras frecuentes identificadas")
    print(f"   → Mostrando top {min(5, len(frequent_words))} palabras:")
    for word, count in frequent_words[:5]:
        print(f"      • {word}: {count} apariciones")

    print_section("Agregando wikilinks a los archivos")
    print(f"   → Procesando {len(markdown_files)} archivos...")

    modified_count = 0
    unchanged_count = 0

    for md_file in markdown_files:
        if process_markdown_file(md_file, words_to_link):
            modified_count += 1
        else:
            unchanged_count += 1

    # Preparar estadísticas para el resumen
    stats = {
        "total_files": len(markdown_files),
        "modified_files": modified_count,
        "unchanged_files": unchanged_count,
        "words_linked": len(words_to_link),
        "top_words": frequent_words,
        "min_length": MIN_WORD_LENGTH,
        "min_freq": MIN_FREQUENCY,
        "top_n": TOP_N_WORDS,
    }

    print(f"   ✓ Procesamiento completado")
    print(f"      • Modificados: {modified_count}")
    print(f"      • Sin cambios: {unchanged_count}")

    print_summary(stats)


if __name__ == "__main__":
    main()
