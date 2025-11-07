# PHD-Notion-to-Obsidian

Herramienta para migrar contenido desde Notion a Obsidian, convirtiendo ideas y notas en archivos Markdown enriquecidos con wikilinks automáticos para mejorar la visualización del grafo de conocimiento.

## Autor

**Frney Córdoba Canchala**

## Descripción

Este proyecto facilita la migración de contenido desde Notion hacia Obsidian mediante dos scripts principales:

1. **Conversión CSV → Markdown**: Transforma exportaciones CSV de Notion en archivos Markdown compatibles con Obsidian, preservando metadatos, tags y conexiones.

2. **Enriquecimiento automático**: Analiza el contenido generado y crea automáticamente wikilinks `[[...]]` para las palabras más frecuentes, mejorando las conexiones en el grafo de conocimiento de Obsidian.

## Características

- Conversión automática de CSV a Markdown con frontmatter YAML
- Extracción y procesamiento de tags y conexiones
- Generación de wikilinks automáticos basados en frecuencia de palabras
- Filtrado inteligente de stopwords (español e inglés)
- Preservación de metadatos (estado, tipo, fuente)
- Estadísticas detalladas del proceso de conversión

## Requisitos

- Python 3.7 o superior
- pandas >= 1.5.0

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/fecork/notion-to-obsidian.git
cd notion-to-obsidian
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Paso 1: Exportar desde Notion

1. En Notion, exporta tu base de datos o página como CSV
2. Coloca el archivo CSV en la carpeta `ExportBlock-741f5d32-6852-42dd-8e67-3d0a65092959-Part-1/`
3. Asegúrate de que el archivo tenga las columnas esperadas:
   - `📝 Idea`: Contenido principal de la idea
   - `🏷️ Tags`: Tags separados por comas o punto y coma
   - `🔗 Conexiones`: Conexiones con otras ideas (texto entre comillas se convierte en wikilinks)
   - `Estado`: Estado de la idea
   - `💡 Tipo`: Tipo de idea
   - `📚 Fuente`: Fuente de la idea

### Paso 2: Generar archivos Markdown

Ejecuta el script de conversión:

```bash
python script_notas.py
```

Este script:
- Lee el archivo CSV especificado en `CSV_PATH`
- Genera archivos Markdown en la carpeta `obsidian_ideas/`
- Crea un frontmatter YAML con metadatos
- Extrae tags y conexiones automáticamente
- Muestra estadísticas del proceso

### Paso 3: Enriquecer con wikilinks automáticos

Después de generar los archivos Markdown, ejecuta el script de enriquecimiento:

```bash
python enriquecer_conexiones.py
```

Este script:
- Analiza todos los archivos Markdown en `obsidian_ideas/`
- Identifica las palabras más frecuentes
- Convierte automáticamente estas palabras en wikilinks `[[...]]`
- Evita crear wikilinks dentro de wikilinks existentes
- Muestra un resumen con las palabras más frecuentes encontradas

## Estructura del Proyecto

```
PHD-Notion-to-Obsidian/
│
├── script_notas.py              # Script principal de conversión CSV → Markdown
├── enriquecer_conexiones.py     # Script de enriquecimiento con wikilinks
├── requirements.txt              # Dependencias del proyecto
├── README.md                    # Este archivo
│
├── ExportBlock-*/               # Carpeta con archivos CSV exportados de Notion
│   └── Ideas *.csv             # Archivo CSV con las ideas
│
└── obsidian_ideas/              # Carpeta de salida con archivos Markdown generados
    └── idea-XXX-*.md           # Archivos Markdown para Obsidian
```

## Configuración

### script_notas.py

Puedes ajustar las siguientes variables al inicio del archivo:

- `CSV_PATH`: Ruta al archivo CSV de entrada
- `OUTPUT_DIR`: Carpeta donde se guardarán los archivos Markdown generados

### enriquecer_conexiones.py

Puedes personalizar el comportamiento del enriquecimiento modificando:

- `INPUT_DIR`: Carpeta donde están los archivos Markdown a procesar (por defecto: `obsidian_ideas`)
- `MIN_WORD_LENGTH`: Longitud mínima de las palabras a considerar (por defecto: 4)
- `MIN_FREQUENCY`: Frecuencia mínima de aparición para convertir en wikilink (por defecto: 2)
- `TOP_N_WORDS`: Número máximo de palabras a convertir en wikilinks (por defecto: 20)
- `STOPWORDS`: Conjunto de palabras a ignorar (ya incluye stopwords comunes en español e inglés)

## Ejemplos

### Ejemplo de salida de script_notas.py

Un archivo Markdown generado tendrá esta estructura:

```markdown
---
id: "idea-001"
title: "Recall y ROC-AUC son métricas más confiables que accuracy"
estado: "En revisión"
tipo: "Métrica"
tags:
  - "evaluación"
  - "métricas"
links:
  - "[[Métricas robustas]]"
---

## Idea

Recall y ROC-AUC son métricas más confiables que accuracy en casos de desbalance de clases.

## Conexiones (texto original)

Conectar con "Métricas robustas"
```

### Ejemplo de enriquecimiento

Antes del enriquecimiento:
```markdown
Los modelos de deep learning requieren validación cruzada para evitar overfitting.
```

Después del enriquecimiento (si "modelos", "deep", "learning", "validación" son palabras frecuentes):
```markdown
Los [[modelos]] de [[deep]] [[learning]] requieren [[validación]] cruzada para evitar overfitting.
```

## Notas Técnicas

- Los archivos se procesan con codificación UTF-8
- El frontmatter YAML se preserva durante el enriquecimiento
- Los wikilinks existentes no se modifican
- Las palabras se normalizan a minúsculas para el análisis
- Se filtran automáticamente palabras muy comunes (stopwords)

## Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo y modificarlo según tus necesidades.

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún problema o tienes sugerencias, por favor abre un issue en el repositorio.

