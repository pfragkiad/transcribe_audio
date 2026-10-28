"""Small desktop form for converting Hanzi to dictionary Pinyin."""

import tkinter as tk
import unicodedata
import webbrowser
from urllib.parse import urlencode
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from mandarin_transcript.pinyin import annotate_hanzi, hanzi_to_pinyin
from mandarin_transcript.dictionary import dictionary_definitions


OUTPUT_MODES = (
    "Pinyin only",
    "Hanzi + Pinyin per word",
    "Hanzi + Pinyin for whole expression",
    "Hanzi + Pinyin on two rows",
)


def format_output(text, mode):
    if mode == OUTPUT_MODES[1]:
        return annotate_hanzi(text)
    if mode in (OUTPUT_MODES[2], OUTPUT_MODES[3]):
        expression = " ".join(text.split())
        if mode == OUTPUT_MODES[3]:
            return f"{expression}\n{hanzi_to_pinyin(expression)}" if expression else ""
        return f"{expression} ({hanzi_to_pinyin(expression)})" if expression else ""
    return hanzi_to_pinyin(text)


def main():
    root = tk.Tk()
    root.title("Hanzi to Pinyin")
    root.geometry("1200x760")
    root.minsize(900, 560)

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=2, uniform="content", minsize=420)
    frame.columnconfigure(1, weight=3, uniform="content")
    frame.rowconfigure(4, weight=1)

    ttk.Label(frame, text="Enter or paste Hanzi:").grid(sticky="w")
    source = ScrolledText(frame, wrap="word", width=1, height=4, font=("KaiTi", 24))
    source.grid(row=1, column=0, sticky="nsew", pady=(6, 12))

    controls = ttk.Frame(frame)
    controls.grid(row=2, column=0, sticky="ew")
    mode = tk.StringVar(value=OUTPUT_MODES[0])
    append_output = tk.BooleanVar(value=False)
    status = tk.StringVar(value="Dictionary readings with tone marks. Ctrl+Enter to convert.")

    options = ttk.Frame(frame)
    options.grid(row=3, column=0, sticky="ew", pady=(12, 6))
    ttk.Label(options, text="Output:").pack(side="left", padx=(0, 8))
    selector = ttk.Combobox(options, textvariable=mode, values=OUTPUT_MODES, state="readonly", width=38)
    selector.pack(side="left", fill="x", expand=True)
    output = ScrolledText(frame, wrap="word", width=1, height=7, font=("Segoe UI", 18), undo=True)
    output.tag_configure("hanzi", font=("KaiTi", 18))

    def select_all(event=None):
        output.tag_add("sel", "1.0", "end-1c")
        return "break"

    output.bind("<Control-a>", select_all)
    menu = tk.Menu(output, tearoff=False)
    for label, action in (("Cut", "<<Cut>>"), ("Copy", "<<Copy>>"), ("Paste", "<<Paste>>")):
        menu.add_command(label=label, command=lambda action=action: output.event_generate(action))
    menu.add_separator()
    menu.add_command(label="Select All", command=select_all)

    def show_menu(event):
        output.focus_set()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    output.bind("<Button-3>", show_menu)
    output.grid(row=4, column=0, sticky="nsew")
    ttk.Label(frame, text="CC-CEDICT word definitions:").grid(
        row=0, column=1, sticky="w", padx=(16, 0)
    )
    definitions_box = ScrolledText(frame, wrap="word", width=1, height=7, font=("Segoe UI", 14), undo=True)
    definitions_box.tag_configure("hanzi", font=("KaiTi", 18))
    definitions_box.grid(row=1, column=1, rowspan=4, sticky="nsew", padx=(16, 0), pady=(6, 0))
    ttk.Label(frame, textvariable=status).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def copy_definitions():
        text = definitions_box.get("1.0", "end-1c")
        if text:
            root.clipboard_clear()
            root.clipboard_append(text)
            status.set("Copied CC-CEDICT definitions to clipboard.")

    definitions_menu = tk.Menu(definitions_box, tearoff=False)
    for label, action in (("Cut", "<<Cut>>"), ("Copy", "<<Copy>>"), ("Paste", "<<Paste>>")):
        definitions_menu.add_command(label=label, command=lambda action=action: definitions_box.event_generate(action))

    def show_definitions_menu(event):
        definitions_box.focus_set()
        try:
            definitions_menu.tk_popup(event.x_root, event.y_root)
        finally:
            definitions_menu.grab_release()
        return "break"

    definitions_box.bind("<Button-3>", show_definitions_menu)

    def set_output(text, append=False, box=output):
        if not append:
            box.delete("1.0", "end")
        elif text and box.get("1.0", "end-1c"):
            box.insert("end", "\n", ())
        for character in text:
            tags = ("hanzi",) if unicodedata.name(character, "").startswith("CJK") else ()
            box.insert("end", character, tags)
        box.see("end")

    def convert(event=None):
        try:
            text = source.get("1.0", "end-1c")
            result = format_output(text, mode.get())
            definitions = dictionary_definitions(text)
            set_output(result, append=append_output.get())
            set_output(definitions.removeprefix("CC-CEDICT word definitions:\n"),
                       append=append_output.get(), box=definitions_box)
            status.set("Converted with offline CC-CEDICT definitions. Select text or use Copy output.")
        except Exception as exc:
            messagebox.showerror("Conversion failed", str(exc), parent=root)
        return "break"

    def copy():
        text = output.get("1.0", "end-1c")
        if text:
            root.clipboard_clear()
            root.clipboard_append(text)
            status.set("Copied to clipboard.")

    def clear():
        source.delete("1.0", "end")
        set_output("")
        set_output("", box=definitions_box)
        status.set("Enter or paste Hanzi to begin.")
        source.focus_set()

    def translate_online():
        text = source.get("1.0", "end-1c").strip()
        if not text:
            status.set("Enter or paste Hanzi before opening Google Translate.")
            source.focus_set()
            return
        query = urlencode({"sl": "zh-CN", "tl": "en", "text": text, "op": "translate"})
        try:
            if not webbrowser.open("https://translate.google.com/?" + query):
                raise RuntimeError("Could not open your default browser.")
            status.set("Opened input text in Google Translate.")
        except Exception as exc:
            messagebox.showerror("Could not open Google Translate", str(exc), parent=root)

    footer = ttk.Frame(frame)
    footer.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))
    ttk.Button(footer, text="Open in Google Translate", command=translate_online).pack(side="left")
    ttk.Button(footer, text="Copy definitions", command=copy_definitions).pack(side="left", padx=8)

    ttk.Button(controls, text="Convert", command=convert).pack(side="left")
    ttk.Button(controls, text="Copy output", command=copy).pack(side="left", padx=8)
    ttk.Button(controls, text="Clear", command=clear).pack(side="left")
    ttk.Checkbutton(controls, text="Append output", variable=append_output).pack(side="left", padx=8)
    selector.bind("<<ComboboxSelected>>", convert)
    root.bind("<Control-Return>", convert)
    source.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
