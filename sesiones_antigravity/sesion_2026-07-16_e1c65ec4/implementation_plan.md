# Plan de Implementación — Respaldo de Memorias de Sesión en GitHub

Este plan detalla el proceso para extraer, estructurar y respaldar el historial completo de las sesiones (conversaciones, transcripciones y artefactos) de Antigravity en tu repositorio de GitHub [UDLA_Proyecto_Integrador_v2.0_Antigravity](https://github.com/villegates/UDLA_Proyecto_Integrador_v2.0_Antigravity.git).

## User Review Required

> [!IMPORTANT]
> - El script leerá el directorio local de datos de la aplicación de Antigravity (`C:\Users\Pablo Villegas\.gemini\antigravity-ide\brain`). Esto contiene los registros crudos de tus conversaciones con la IA.
> - Al subirlos a GitHub, las transcripciones y consultas se guardarán en un formato estructurado y legible en Markdown, además de sus archivos JSONL y artefactos.
> - Por favor, asegúrate de que el repositorio sea privado si las conversaciones contienen información sensible o credenciales (ya verificamos que el `.env` anterior se removió del historial activo, pero siempre es bueno tener precaución).

## Propuesta de Cambios y Estructura

Crearemos un script de automatización en Python en la carpeta de scratch para realizar la extracción y copia. Los archivos se guardarán en una nueva carpeta dentro del repositorio de Antigravity:

`c:\Users\Pablo Villegas\OneDrive\Documents\Claude\UDLA\Modulo 2\Antigravity\sesiones_antigravity\`

### Estructura de Carpetas Generada:

```
Antigravity/
└── sesiones_antigravity/
    ├── README.md (Índice general de todas las sesiones con fechas y solicitudes iniciales)
    └── sesion_<FECHA>_<ID_CORTO>/
        ├── README.md (Resumen estructurado de la conversación: consultas del usuario, planes y herramientas utilizadas)
        ├── transcript.jsonl (Registro crudo resumido)
        ├── transcript_full.jsonl (Registro crudo completo)
        └── [Artefactos de la sesión] (Si existen: implementation_plan.md, task.md, walkthrough.md, etc.)
```

### Componentes y Archivos

#### [NEW] [backup_sessions.py](file:///c:/Users/Pablo%20Villegas/OneDrive/Documents/Claude/UDLA/Modulo%202/Antigravity/backup_sessions.py)
Un script de Python que automatiza:
1. El escaneo de la carpeta `brain` de Antigravity.
2. La extracción de metadatos (fechas, prompts de usuario, respuestas clave).
3. La generación de los informes de Markdown legibles por humanos (`README.md` de cada sesión).
4. La copia de las transcripciones y artefactos correspondientes.
5. Un índice global de sesiones en el directorio raíz del respaldo.

## Plan de Verificación y Despliegue

### Pasos de Ejecución
1. **Creación del Script**: Escribir `backup_sessions.py` dentro de `Antigravity`.
2. **Ejecución Local**: Correr el script para generar la carpeta `sesiones_antigravity`.
3. **Revisión del Índice**: Inspeccionar el archivo `README.md` de índice generado para verificar que sea correcto.
4. **Push a GitHub**:
   ```powershell
   git add sesiones_antigravity/
   git commit -m "docs: respaldar historial completo de sesiones de Antigravity"
   git push origin main
   ```

### Verificación Manual
- Te pediré confirmar que puedas visualizar correctamente el índice y las carpetas de las sesiones en tu repositorio de GitHub una vez realizado el push.
