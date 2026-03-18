# Changelog - Surya OCR PRO

## [3.0.0] - 2026-03-18

### Migrazione motore OCR: DeepSeek -> Surya/marker-pdf
- **Sostituzione completa** del motore OCR: rimosso DeepSeek VLM, adottato marker-pdf (Surya)
- **Qualita' OCR nettamente superiore**: nomi scientifici in corsivo preservati, struttura markdown corretta, testo italiano fluido
- **Layout analysis avanzato**: riconoscimento tabelle, heading, ordine di lettura - critico per chiavi dicotomiche
- **90+ lingue supportate** nativamente (italiano, latino, inglese, etc.)
- **Nessun download manuale del modello**: Surya scarica automaticamente i modelli al primo avvio (~2 GB vs 6.2 GB di DeepSeek)
- **Nessuna dipendenza da transformers/tokenizers**: rimossi vincoli di versione rigidi

### Semplificazioni
- Rimossi parametri DeepSeek-specifici: `--mode`, `--quantize`, `--device`, `--model-path`, `--prompt`, `--max-tokens`, `--setup`
- Aggiunto parametro `--languages` per specificare le lingue OCR (default: `it,la`)
- Aggiunto parametro `--no-force-ocr` per PDF con testo digitale
- Semplificato text post-processor (output marker-pdf e' gia' pulito, non servono filtri anti-allucinazione)
- Rimossi file modello DeepSeek dalla directory `models/`
- Rimosso script `scripts/download_model.py` (non piu' necessario)

### Dipendenze
- **Aggiunta**: `marker-pdf>=1.10` (include surya-ocr automaticamente)
- **Rimosse**: `torch` (diretto), `transformers`, `tokenizers`, `einops`, `easydict`, `addict`, `safetensors`, `huggingface_hub`
- **Mantenute**: `PyMuPDF`, `Pillow`, `python-docx`, `pyyaml`, `tqdm`

### Note per utenti V2
- Il sistema di checkpoint e' compatibile: i job interrotti con V2 possono essere ripresi con V3
- I formati di output (TXT, Markdown, DOCX) sono identici
- La GUI e' stata aggiornata ma mantiene lo stesso layout

---

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
