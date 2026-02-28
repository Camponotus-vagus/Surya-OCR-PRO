# Changelog - DeepSeek OCR PRO V2

## [2.0.0] - 2026-02-28

### Architettura
- **Riscrittura completa** da GUI-only monolite a architettura CLI-first modulare
- **Architettura a layer**: Engine -> Pipeline -> CLI -> GUI (opzionale)
- Eliminata architettura subprocess (V1 lanciava `run_ocr_custom.py` come processo separato)
- Ogni modulo ha responsabilita' singola e puo' essere testato indipendentemente

### Ottimizzazioni Performance (CPU Intel)
- **float32 nativo** invece di bfloat16 emulato su CPU Intel (1.5-2x speedup)
- **INT8 dynamic quantization** su layer lineari del language model (2-4x speedup)
- **Thread tuning**: 8 thread = core fisici per evitare overhead hyperthreading
- **Pipeline prefetch**: pre-estrazione pagine in background mentre il modello processa
- **Estrazione diretta** immagini embedded da PDF con PyMuPDF (no re-rasterizzazione)
- **torch.autocast patch**: forza float32 su CPU per compatibilita' con INT8

### Bug Fix Critici
- **Fix V1 bug `infer()` return None**: V1 chiamava `model.infer()` senza `eval_mode=True`,
  il metodo non ritornava testo ma `None`. V2 usa `eval_mode=True` che ritorna il testo decodificato.
- Rimossa dipendenza da `pdf2image` + poppler (sostituita con PyMuPDF, zero dipendenze esterne)
- Fix gestione path con spazi e caratteri speciali (accenti, etc.)

### Nuove Feature
- **CLI completa** con argparse: `deepseek-ocr [OPTIONS] INPUT...`
- **Output Markdown**: preserva la formattazione markdown generata dal modello
- **Estrazione immagini**: embedded dal PDF + regioni rilevate dal modello (grounding)
- **Sistema checkpoint/resume**: salva risultati per-pagina, riprende dopo interruzioni
- **File di configurazione**: supporto YAML/JSON per salvare impostazioni
- **Logging strutturato**: file + console con livelli configurabili
- **Cancellazione**: pulsante Cancel nella GUI per interrompere l'elaborazione

### Dipendenze
- **Rimossa**: `pdf2image`, poppler (dipendenza sistema)
- **Aggiunta**: `PyMuPDF` (fitz) - PDF handling puro Python, cross-platform
- **Aggiunta**: `pyyaml` - file di configurazione
- **Opzionale**: `customtkinter` - solo per la GUI

### Testing
- 86 unit test con pytest (tutti passano)
- Coverage: config, PDF handler, checkpoint, text post-processing, CLI, output writers, image extractor
- Test per edge case: path con spazi, Unicode, file bloccati, pagine corrotte
- **Test end-to-end** con PDF reali (Carabidi 1 Natura.pdf, pagina 6):
  - Pipeline completa funzionante: PDF -> estrazione pagina -> OCR -> output
  - Modo `fast` (640px): qualita' insufficiente per scansioni B&W dense (~200 DPI).
    Il testo viene downscalato troppo aggressivamente. Usare sempre `accurate` per questi PDF.
  - Modo `accurate` (1024px + crop): qualita' ottimale per documenti scansionati
  - torch.autocast patch verificato: risolve conflitto bfloat16/INT8 su CPU Intel

### Distribuzione
- Struttura progetto Python moderna con `pyproject.toml` (PEP 621)
- `.gitignore` completo
- Pronto per GitHub Actions CI/CD
- Configurazione PyInstaller per build standalone (Windows, macOS, Linux)
- Modello scaricato separatamente al primo avvio (non incluso nell'eseguibile)

### Confronto V1 vs V2
| Aspetto | V1 | V2 |
|---------|----|----|
| Interfaccia | Solo GUI | CLI + GUI opzionale |
| Output | TXT, DOCX | TXT, TXT/pagina, DOCX, **Markdown** |
| Immagini | Non implementato | **Embedded + grounding** |
| Resume | No | **Checkpoint per-pagina** |
| Performance CPU | bfloat16 emulato | **float32 + INT8 quantization** |
| PDF library | pdf2image + poppler | **PyMuPDF (zero deps esterne)** |
| Test | 0 | **86 test** |
| Dipendenze esterne | poppler (sistema) | **Nessuna** |
