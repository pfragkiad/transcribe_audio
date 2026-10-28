# Mandarin/English transcription

Run the existing entry point:

Edit the settings at the top of `run_transcript.ps1`, then run it without arguments:

```powershell
.\run_transcript.ps1
```

The default settings select `CD1 Lesson 1.mp3`, mixed mode, inline Pinyin, and TXT.
All other examples remain as comments inside the script.

To process every MP3 directly inside a directory, edit `$InputDirectory`,
`$Extension`, and the other settings at the top of
`run_transcript_directory.ps1`, then run it without arguments:

```powershell
.\run_transcript_directory.ps1
```

Both PowerShell runners have no command-line parameters. All configuration is
inside the scripts, with examples kept as comments. The directory runner
accepts `mp3` or `.mp3` in `$Extension`, ignores extension case, and processes
files in filename order without entering subdirectories. Set `$ListOnly = $true`
to preview matching files. Each input writes one UTF-8 file directly into
`output/`. Failed files are reported while the remaining files continue.
Optionally set `$TargetDirectory = 'D:\results'` inside the directory runner
to move each completed result there, replacing a same-named result if present.
Leave it empty to keep results in `output/`.
Relative target paths are resolved against `$InputDirectory`; for example,
`$TargetDirectory = 'results'` moves files into `<input directory>/results/`.

Or use Python directly:

```powershell
python transcript.py recording.mp3 --device auto --mode mixed
```

You can also use `python -m mandarin_transcript` with the same arguments.
The default model is `large-v3`. Each run writes exactly one UTF-8 file
under `output/<input name>.<format>`, preserving the recognized Chinese/English text.
Use `--output-dir PATH` to choose a different output root.
The CLI always configures standard input, output, and error as UTF-8, including
redirected output on Windows. All generated TXT/SRT files use explicit UTF-8.
No `-X utf8` flag is needed.

`transcript.py` owns `main()`: argument parsing, input validation, transcription
pass, CPU fallback, and progress reporting. It calls reusable components:

| Module | Responsibility |
| --- | --- |
| `runtime.py` | Windows NVIDIA DLL discovery |
| `device.py` | Device and compute-type selection |
| `transcription.py` | Model loading and Whisper transcription options |
| `output.py` | Transcript and subtitle serialization |
| `pinyin.py` | Reusable Hanzi-to-dictionary-Pinyin conversion |

Inference dependencies load only when transcription or device detection needs
them, so CLI help and output utilities can run without loading Whisper.

## Pinyin output

The desktop form always includes offline CC-CEDICT word definitions when
converting Hanzi, in every Pinyin output mode. It looks up longest matching
words and lists all available readings and meanings; these are dictionary
definitions, not a sentence translation. The dictionary must be present at
`data/cedict/cedict_ts.u8`. Missing entries are explicitly marked.
The **Open in Google Translate** button additionally opens the original
input in your browser for Chinese-to-English translation.

CC-CEDICT is published by MDBG and maintained by the CC-CEDICT community,
under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
See the [dictionary source](https://www.mdbg.net/chinese/dictionary?page=cedict)
and local `data/cedict/README.md` for attribution and download details.

For a desktop form, double-click `pinyin_form.pyw` in the project folder.
Paste Hanzi and click **Convert** (or press **Ctrl+Enter**). Use **Copy output**
to copy the result. Choose **Pinyin only**, **Hanzi + Pinyin per word**, or
**Hanzi + Pinyin for whole expression**, or **Hanzi + Pinyin on two rows**
in the Output dropdown. The two-row option places Hanzi above Pinyin without parentheses.
The launcher uses the project's `.venv`; no transcription model is loaded.
You can also launch it with `.venv\Scripts\python.exe -m mandarin_transcript.pinyin_form`.

Install dependencies with `pip install -r requirements.txt`, then run:

```powershell
python transcript.py recording.mp3 --pinyin
```

Choose one mode (`mixed`, the default, or `chinese`) and one format
(`txt`, the default, or `srt`). Each invocation writes exactly one file:

| Options | Output file |
| --- | --- |
| `--mode mixed` | `output/recording.txt` |
| `--mode mixed --pinyin` | `output/recording.txt` |
| `--mode chinese` | `output/recording.txt` |
| `--mode chinese --pinyin` | `output/recording.txt` |
| `--mode chinese --pinyin --format srt` | `output/recording.srt` |

In PowerShell, edit `$Mode`, `$Pinyin`, and `$Format` inside `run_transcript.ps1`.

Pinyin output contains merged Chinese and Pinyin: `你好(nǐ hǎo)，世界(shì jiè)！`.
The filename uses the input stem regardless of mode or Pinyin. Running again
with the same input and format overwrites that output file.

Jieba segments Chinese words; PyPinyin adds tone-marked readings after each word
in parentheses. Source segment text and subtitle timing are preserved,
as are English and punctuation. Word boundaries are inferred and may need
adjustment for names or ambiguous phrases.
It provides dictionary readings without tone sandhi; spoken pronunciation
processing remains a separate future stage.

The converter also works independently of Whisper:

```python
from mandarin_transcript.pinyin import annotate_hanzi

print(annotate_hanzi("你好，世界！"))  # 你好(nǐ hǎo)，世界(shì jiè)！
```
