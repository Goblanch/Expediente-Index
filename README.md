# Expediente-Index
Pequeña aplicación de escritorio (Tkinter + ttkbootstrap) para generar un **Índice de Documentos** a partir de todos los **PDF** de una carpeta, exportando a **Word (.docx)** y/o **PDF (.pdf)**.

> **Estado**: MVP funcional en `main`. Próximas mejoras en ramas de feature.
> **Descarga**: por ahora no hay binarios públicos; compila localmente (ver Build.exe)
> **English?** See [README.en.md](./README.en.MD)

---

## ¿Por qué existe esta herramienta?

La idea nace de una necesidad real: **mi hermana, abogada**, me explicó que al presentar un conjunto de documentos legales se crea **un índice** (una primera hoja con los nombres de todos los documentos) **de forma manual**, **ExpedienteIndex** automatiza ese paso: toma todos los PDF de una carpeta y genera un índice limpio en Word o PDF.

En el contexto del **sistema judicial español**, es habitual acompañar escritos y documentación con un **índice** para facilitar la consulta y la revisión del expediente por parte del juzgado y de las demás partes. No sustituye a ningún formato oficial ni valida contenido jurídico; simplemente agiliza la **puesta en orden** de los documentos presentados.

---

## Características (MVP)

- Selección de carpeta con documentos **PDF**.
- Vista previa de títulos (nombre de archivo sin extensión).
- Exportación a **Word (.docx)** y/o **PDF (.pdf)**.
- Interfaz sencilla con **Tkinter** y **ttkbootstrap**.

---

## Roadmap (próximas mejoras)

- **Selector de fuente** (según las instaladas en el sistema).
- Opciones de **cabecera**: mostrar/ocultar **título** y **fecha**, **tamaño**, **alineación** y **título editable**.
- **Prederencias por defecto**: Word activado por defecto, PDF desactivado por defecto.
- (Futuro) Plantillas personalizadas (logo, márgenes corporativos), CLI y configuración persistente.

---

## Instalación (desde código)

Requisitos:
- **Python 3.10+**
- Windows/macOS/Linux

```bash
# Clonar
git clone httpshttps://github.com/Goblanch/Expediente-Index.git
cd ExpedienteIndex

# Entorno virtual (recomendado)
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

# Dependencias
pip install -r requirements.txt

# (Opcional) instalar el paquete en modo editable
pip install e .
```

Ejecutar la app:
```bash
python -m expedienteindex
```

Tests
```bash
# Dependencias de test
pip install pytest pypdf

# Ejecutar
pytest -q
```

---

## Estructura del proyecto

```bash
ExpedienteIndex/
├─ src/
│  └─ expedienteindex/
│     ├─ __init__.py
│     ├─ __main__.py        # ejecutar con: python -m expedienteindex
│     ├─ app.py             # UI Tkinter + ttkbootstrap
│     ├─ indexing.py        # descubrimiento/ordenación de PDFs
│     └─ exporters.py       # export a DOCX/PDF
├─ tests/
│  ├─ test_indexing.py
│  └─ test_exporters.py
├─ entrypoint.py            # punto de entrada para PyInstaller
├─ requirements.txt
└─ README.md

```

---

## Contribuir

Branching:
- `main`: estabe
- `feature/<nombre>`: una mejora o bug fix por rama
- (Opcional) `develop`: integración previa a `main`

Estilo de commits (recomendado):
- `feat`: nueva funcionalidad.
- `fix`: corrección.
- `refactor`: cambios internos.
- `docs`: documentación.
- `tests`
- `build/chore`: tooling, CI, empaquetado.

Ejemplos:

```text
feat(ui): add header config (title text, show/hide date, sizes, align)
feat(fonts): allow selecting system fonts for title and body
feat(export): apply header options to docx and pdf export
fix(ui): correct ttkbootstrap style typos and list insertion
```