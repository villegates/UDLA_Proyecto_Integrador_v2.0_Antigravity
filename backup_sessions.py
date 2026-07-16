import os
import shutil
import json
from datetime import datetime

brain_dir = r"C:\Users\Pablo Villegas\.gemini\antigravity-ide\brain"
repo_root = r"c:\Users\Pablo Villegas\OneDrive\Documents\Claude\UDLA\Modulo 2\Antigravity"
backup_root = os.path.join(repo_root, "sesiones_antigravity")

os.makedirs(backup_root, exist_ok=True)

sessions_data = []

for folder in os.listdir(brain_dir):
    folder_path = os.path.join(brain_dir, folder)
    if not os.path.isdir(folder_path) or folder == "tempmediaStorage":
        continue
    
    # Paths
    logs_dir = os.path.join(folder_path, ".system_generated", "logs")
    transcript_path = os.path.join(logs_dir, "transcript.jsonl")
    transcript_full_path = os.path.join(logs_dir, "transcript_full.jsonl")
    
    date_str = None
    first_request = "No initial request found"
    steps = []
    
    if os.path.exists(transcript_path):
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    step = json.loads(line)
                    steps.append(step)
                    
                    if step.get("type") == "USER_INPUT" and date_str is None:
                        created_at = step.get("created_at", "")
                        if created_at:
                            date_str = created_at
                            # Extract prompt
                            content = step.get("content", "")
                            if "<USER_REQUEST>" in content:
                                start = content.find("<USER_REQUEST>") + len("<USER_REQUEST>")
                                end = content.find("</USER_REQUEST>")
                                first_request = content[start:end].strip()
                            else:
                                first_request = content.strip()
        except Exception as e:
            print(f"Error reading transcript for {folder}: {e}")
            
    # Format date for folder name
    if date_str:
        try:
            # Parse ISO timestamp (e.g. 2026-06-27T12:26:30Z)
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            folder_date = dt.strftime("%Y-%m-%d")
            display_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            folder_date = "unknown_date"
            display_date = date_str
    else:
        folder_date = "unknown_date"
        display_date = "Unknown Date"
        
    id_short = folder[:8]
    session_folder_name = f"sesion_{folder_date}_{id_short}"
    session_backup_dir = os.path.join(backup_root, session_folder_name)
    os.makedirs(session_backup_dir, exist_ok=True)
    
    # Copy JSONL files
    for src_file in [transcript_path, transcript_full_path]:
        if os.path.exists(src_file):
            shutil.copy(src_file, session_backup_dir)
            
    # Copy artifacts (.md files in the folder)
    artifacts_copied = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.endswith(".md"):
            shutil.copy(file_path, session_backup_dir)
            artifacts_copied.append(file)
            
    # Also check browser/ subfolder for scratchpad files if any
    browser_dir = os.path.join(folder_path, "browser")
    if os.path.exists(browser_dir):
        browser_backup_dir = os.path.join(session_backup_dir, "browser")
        os.makedirs(browser_backup_dir, exist_ok=True)
        for file in os.listdir(browser_dir):
            file_path = os.path.join(browser_dir, file)
            if os.path.isfile(file_path) and file.endswith(".md"):
                shutil.copy(file_path, browser_backup_dir)
                
    # Build README.md for this session
    session_readme_path = os.path.join(session_backup_dir, "README.md")
    
    # Process steps for readability
    user_prompts = []
    tool_calls_summary = []
    
    for step in steps:
        step_type = step.get("type")
        step_source = step.get("source")
        
        if step_type == "USER_INPUT":
            content = step.get("content", "")
            if "<USER_REQUEST>" in content:
                start = content.find("<USER_REQUEST>") + len("<USER_REQUEST>")
                end = content.find("</USER_REQUEST>")
                prompt = content[start:end].strip()
            else:
                prompt = content.strip()
            user_prompts.append(prompt)
            
        elif step_type == "PLANNER_RESPONSE" or step_source == "MODEL":
            # Extract tool calls
            t_calls = step.get("tool_calls", [])
            if t_calls:
                for tc in t_calls:
                    name = tc.get("name", "unknown")
                    args = tc.get("args", {})
                    # Get summary if present
                    summary = args.get("toolSummary", "")
                    tool_calls_summary.append((name, summary))
                    
    # Generate the Markdown representation
    session_markdown = []
    session_markdown.append(f"# Sesión de Antigravity — {id_short}\n")
    session_markdown.append(f"- **ID Completo:** `{folder}`\n")
    session_markdown.append(f"- **Fecha:** {display_date}\n\n")
    session_markdown.append("## 📥 Solicitud Inicial\n\n")
    session_markdown.append("```text\n")
    session_markdown.append(first_request + "\n")
    session_markdown.append("```\n\n")
    
    if user_prompts:
        session_markdown.append("## 💬 Historial de Interacciones (Prompts del Usuario)\n\n")
        for idx, p in enumerate(user_prompts, 1):
            session_markdown.append(f"### Interacción {idx}\n\n")
            session_markdown.append(f"{p}\n\n")
            
    if tool_calls_summary:
        session_markdown.append("## 🛠️ Herramientas Utilizadas\n\n")
        session_markdown.append("| Herramienta | Acción / Resumen |\n")
        session_markdown.append("|---|---|\n")
        last_pair = None
        for name, summary in tool_calls_summary:
            if (name, summary) != last_pair:
                session_markdown.append(f"| `{name}` | {summary} |\n")
                last_pair = (name, summary)
        session_markdown.append("\n")
        
    if artifacts_copied:
        session_markdown.append("## 📄 Artefactos Generados\n\n")
        for art in artifacts_copied:
            # For the consolidated file, we point to the folders, but for the session readme we point to local files.
            # We'll write the local relative links to the individual session README
            pass
            
    # Write session README
    with open(session_readme_path, 'w', encoding='utf-8') as rf:
        rf.write("".join(session_markdown))
        if artifacts_copied:
            rf.write("## 📄 Artefactos Generados\n\n")
            for art in artifacts_copied:
                rf.write(f"- [{art}]({art})\n")
            rf.write("\n")
            
    sessions_data.append({
        "id": folder,
        "id_short": id_short,
        "date_sort": date_str or "0000-00-00",
        "date_display": display_date,
        "folder_name": session_folder_name,
        "first_request": first_request,
        "markdown_body": "".join(session_markdown),
        "artifacts": artifacts_copied
    })

# Sort sessions by date descending
sessions_data.sort(key=lambda x: x["date_sort"], reverse=True)

# Generate main index README.md inside the folder
index_readme_path = os.path.join(backup_root, "README.md")
with open(index_readme_path, 'w', encoding='utf-8') as f:
    f.write("# 🧠 Historial de Sesiones de Antigravity\n\n")
    f.write("Este repositorio contiene el respaldo de todas las sesiones de trabajo con la IA Antigravity. ")
    f.write("Cada carpeta incluye los registros crudos de transcripción (`transcript.jsonl` y `transcript_full.jsonl`), ")
    f.write("los artefactos generados durante la sesión, y un resumen en formato Markdown para facilitar la lectura.\n\n")
    
    f.write("## 📌 Índice de Sesiones\n\n")
    f.write("| Fecha | Sesión | Solicitud Inicial / Resumen |\n")
    f.write("|---|---|---|\n")
    
    for s in sessions_data:
        req_trunc = s["first_request"].replace("\n", " ").strip()
        if len(req_trunc) > 150:
            req_trunc = req_trunc[:147] + "..."
        f.write(f"| {s['date_display'][:10]} | [{s['id_short']}]({s['folder_name']}/README.md) | {req_trunc} |\n")

# Generate consolidated MEMORIA_COMPLETA_SESIONES.md at the repository root
consolidated_path = os.path.join(repo_root, "MEMORIA_COMPLETA_SESIONES.md")
with open(consolidated_path, 'w', encoding='utf-8') as f:
    f.write("# 🧠 Memoria Completa de Sesiones de Antigravity\n\n")
    f.write("Este archivo contiene el historial unificado y completo de todas las sesiones de trabajo con Antigravity en este proyecto.\n\n")
    
    f.write("## 📌 Índice de Sesiones\n\n")
    f.write("| Fecha | Sesión | Solicitud Inicial / Resumen | Enlace al Resumen Individual |\n")
    f.write("|---|---|---|---|\n")
    
    for s in sessions_data:
        req_trunc = s["first_request"].replace("\n", " ").strip()
        if len(req_trunc) > 100:
            req_trunc = req_trunc[:97] + "..."
        f.write(f"| {s['date_display'][:10]} | [{s['id_short']}](#sesión-de-antigravity--{s['id_short']}) | {req_trunc} | [Ir a Carpeta](sesiones_antigravity/{s['folder_name']}/README.md) |\n")
        
    f.write("\n---\n\n")
    
    # Write the full body of each session
    for s in sessions_data:
        f.write(s["markdown_body"])
        
        # Include artifact links relative to root/sesiones_antigravity/sesion_.../
        if s["artifacts"]:
            f.write("## 📄 Artefactos Generados\n\n")
            for art in s["artifacts"]:
                f.write(f"- [{art}](sesiones_antigravity/{s['folder_name']}/{art})\n")
            f.write("\n")
            
        f.write("\n---\n\n")
        
print("Backup and consolidated file completed successfully!")
