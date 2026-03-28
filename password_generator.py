#!/usr/bin/env python3
"""
Diceware/BIP39 Password Generator - Secure Local Edition
Default loads: wordlist.txt (rename any wordlist file to this) or manually select the file txt-file
Supports: EFF Diceware (7776 words) and BIP39 (2048 words) automatically
"""

import os
import sys
import secrets
import webbrowser
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Error: Tkinter not installed.")
    sys.exit(1)

class DicewareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator - Diceware & BIP39")
        
        # Set minimum size (matches your minimum.png)
        self.root.minsize(800, 850)
        
        # Start maximized but allow OS controls (no true fullscreen)
        self.root.state('zoomed')
        
        self.root.configure(bg='#f5f5f5')
        
        self.wordlist = {}
        self.loaded = False
        self.wordlist_type = "Unknown"
        self.bits_per_word = 0
        self.current_path = None
        self.default_filename = "wordlist.txt"
        
        self.colors = {
            'bg': '#f5f5f5', 'card': '#ffffff',
            'primary': '#10b981', 'secondary': '#3b82f6',
            'warning': '#fef3c7', 'warning_border': '#f59e0b',
            'info': '#e0f2fe', 'info_border': '#0284c7',
            'success': '#d1fae5', 'error': '#fee2e2',
            'purple': '#f3e8ff', 'purple_border': '#9333ea'
        }
        
        self.create_ui()
        self.auto_load()
        
    def create_ui(self):
        # Create scrollable canvas
        container = tk.Frame(self.root, bg=self.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.main_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        # Make inner frame match canvas width
        def configure_frame(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        self.canvas.bind('<Configure>', configure_frame)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mousewheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # 🔒 SECURITY NOTICE BOX
        sec_frame = tk.Frame(self.main_frame, bg=self.colors['purple'], 
                            highlightbackground=self.colors['purple_border'],
                            highlightthickness=4)
        sec_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(sec_frame, text="🔒 Security Notice", 
                bg=self.colors['purple'], fg='#581c87',
                font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=15, pady=(12, 8))
        
        security_bullets = [
            "• Passwords stay in RAM only. Close app to clear.",
            "• Malware can steal clipboard/keystrokes",
            "• OS may cache clipboard/swap",
            "• It's safer to write password on paper than save on PC",
            "• High security: Run from bootable USB OS (tails)"
        ]
        
        for bullet in security_bullets:
            tk.Label(sec_frame, text=bullet, bg=self.colors['purple'], 
                    fg='#581c87', font=('Segoe UI', 10), justify=tk.LEFT).pack(anchor='w', padx=15)
        
        tk.Label(sec_frame, text="💡 Tip: For crypto wallets, rename bip39-english.txt to wordlist.txt", 
                bg=self.colors['purple'], fg='#581c87', 
                font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=15, pady=(8, 12))
        
        # Error Banner (Hidden initially)
        self.error_frame = tk.Frame(self.main_frame, bg=self.colors['warning'], 
                                   highlightbackground=self.colors['warning_border'],
                                   highlightthickness=4)
        tk.Label(self.error_frame, 
                text=f"Wordlist Not Found: {self.default_filename}\nClick here to download Diceware list from eff.org\n(Or rename BIP39 list to 'wordlist.txt')",
                bg=self.colors['warning'], fg='#92400e',
                font=('Segoe UI', 11, 'bold'), cursor="hand2").pack(pady=12, padx=15)
        self.error_frame.bind("<Button-1>", lambda e: webbrowser.open(
            "https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt"))
        
        # Info Banner
        info = tk.Frame(self.main_frame, bg=self.colors['info'],
                       highlightbackground=self.colors['info_border'],
                       highlightthickness=4)
        info.pack(fill=tk.X, pady=(0, 20))
        info_text = "Supports: EFF Diceware (7776 words, 12.9 bits/word) and BIP39 (2048 words, 11 bits/word)\nAutomatically detects type based on word count."
        tk.Label(info, text=info_text, bg=self.colors['info'], fg='#0c4a6e', 
                font=('Segoe UI', 11)).pack(pady=12, padx=15)
        
        # Status Card
        self.status_card = tk.Frame(self.main_frame, bg=self.colors['card'], bd=0,
                                   highlightbackground='#e5e7eb', highlightthickness=1)
        self.status_card.pack(fill=tk.X, pady=(0, 20), ipady=15)
        
        self.status_label = tk.Label(self.status_card, 
                                    text=f"Looking for {self.default_filename}...",
                                    bg=self.colors['card'], fg='#6b7280', 
                                    font=('Segoe UI', 12))
        self.status_label.pack(pady=5)
        
        self.type_label = tk.Label(self.status_card, text="", 
                                  bg=self.colors['card'], fg='#3b82f6',
                                  font=('Segoe UI', 11, 'bold'))
        self.type_label.pack(pady=2)
        
        # Buttons frame
        btn_frame = tk.Frame(self.status_card, bg=self.colors['card'])
        btn_frame.pack(pady=10)
        
        self.manual_btn = tk.Button(btn_frame, text="Select wordlist.txt Manually",
                                   bg=self.colors['secondary'], fg='white',
                                   font=('Segoe UI', 11), padx=15, pady=8,
                                   cursor='hand2', command=self.manual_load)
        self.manual_btn.pack(side=tk.LEFT, padx=5)
        
        self.switch_btn = tk.Button(btn_frame, text="Load Different Wordlist",
                                 bg=self.colors['secondary'], fg='white',
                                 font=('Segoe UI', 11), padx=15, pady=8,
                                 cursor='hand2', command=self.switch_wordlist,
                                 state=tk.DISABLED)
        self.switch_btn.pack(side=tk.LEFT, padx=5)
        
        # Generator Card
        gen = tk.Frame(self.main_frame, bg=self.colors['card'], bd=0,
                      highlightbackground='#e5e7eb', highlightthickness=1)
        gen.pack(fill=tk.BOTH, expand=True, ipady=20)
        
        tk.Label(gen, text="Configure Passphrase", 
                bg=self.colors['card'], fg='#1f2937',
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', padx=20, pady=(20, 25))
        
        # Word count
        frm = tk.Frame(gen, bg=self.colors['card'])
        frm.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(frm, text="Number of Words", bg=self.colors['card'],
                fg='#374151', font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        
        self.word_count = tk.Spinbox(frm, from_=3, to=50, width=12, font=('Segoe UI', 12),
                                    command=self.update_quantum_note)
        self.word_count.delete(0, tk.END)
        self.word_count.insert(0, "6")
        self.word_count.pack(anchor='w', pady=(8, 0))
        
        # Quantum safety note
        self.quantum_label = tk.Label(frm, text="6 words = 77 bits (Pre-quantum secure)", 
                                     bg=self.colors['card'], fg='#6b7280',
                                     font=('Segoe UI', 10, 'italic'))
        self.quantum_label.pack(anchor='w', pady=(5, 0))
        
        # Separator
        frm2 = tk.Frame(gen, bg=self.colors['card'])
        frm2.pack(fill=tk.X, padx=20, pady=25)
        tk.Label(frm2, text="Separator Style", bg=self.colors['card'],
                fg='#374151', font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        
        self.sep_var = tk.StringVar(value=' ')
        self.sep_options = [
            ("word1 word2 word3  (Space)", " "),
            ("word1-word2-word3  (Hyphen)", "-"),
            ("word1word2word3  (No separator)", ""),
            ("word1.word2.word3  (Dot)", ".")
        ]
        
        for text, val in self.sep_options:
            rb = tk.Radiobutton(frm2, text=text, variable=self.sep_var, value=val,
                              bg=self.colors['card'], fg='#374151',
                              font=('Segoe UI', 11), selectcolor=self.colors['card'])
            rb.pack(anchor='w', pady=4)
        
        # Generate Button
        self.gen_btn = tk.Button(gen, text="Load Wordlist First",
                                bg='#9ca3af', fg='white', 
                                font=('Segoe UI', 14, 'bold'),
                                state=tk.DISABLED, padx=20, pady=12,
                                command=self.generate)
        self.gen_btn.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Output Area - NOW WITH TEXT WIDGET FOR WRAPPING
        self.output_frame = tk.Frame(gen, bg=self.colors['success'],
                                  highlightbackground='#10b981',
                                  highlightthickness=2)
        
        # Changed from Entry to Text for multiline wrapping
        self.pw_text = tk.Text(self.output_frame, font=('Consolas', 16, 'bold'),
                              bg=self.colors['success'], fg='#065f46',
                              relief=tk.FLAT, wrap=tk.WORD, height=3, padx=10, pady=10)
        self.pw_text.pack(fill=tk.X, padx=20, pady=20)
        self.pw_text.config(state=tk.DISABLED)  # Read-only
        
        self.entropy_label = tk.Label(self.output_frame, text="",
                                     bg=self.colors['success'], fg='#065f46',
                                     font=('Segoe UI', 11))
        self.entropy_label.pack(pady=(0, 10))
        
        self.copy_btn = tk.Button(self.output_frame, text="Copy to Clipboard",
                                 bg='#065f46', fg='white', font=('Segoe UI', 11),
                                 padx=15, pady=6, cursor='hand2',
                                 command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=(0, 15))
    
    def auto_load(self):
        """Try multiple locations to find wordlist.txt"""
        script_dir = Path(__file__).parent.absolute()
        current_dir = Path.cwd()
        home_dir = Path.home()
        
        possible_paths = [
            script_dir / self.default_filename,
            current_dir / self.default_filename,
            home_dir / self.default_filename,
            home_dir / "Downloads" / self.default_filename,
        ]
        
        for path in possible_paths:
            if path.exists():
                self.load_wordlist(path)
                return
        
        self.show_error()
    
    def manual_load(self):
        """Open file dialog when auto-load fails"""
        filename = filedialog.askopenfilename(
            title=f"Select {self.default_filename} (or any wordlist)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.load_wordlist(Path(filename))
    
    def switch_wordlist(self):
        """Load a different wordlist without restarting"""
        filename = filedialog.askopenfilename(
            title="Load Different Wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.loaded = False
            self.wordlist = {}
            self.output_frame.pack_forget()
            self.load_wordlist(Path(filename))
    
    def detect_wordlist_type(self, count):
        """Auto-detect if Diceware (7776) or BIP39 (2048)"""
        if count == 7776:
            return "EFF Diceware", 12.925
        elif count == 2048:
            return "BIP39 (Crypto)", 11.0
        elif count > 7000:
            return f"Extended Diceware ({count})", __import__('math').log2(count)
        elif count > 1000:
            return f"Custom/BIP39-like ({count})", __import__('math').log2(count)
        else:
            return f"Short List ({count})", __import__('math').log2(count)
    
    def load_wordlist(self, path):
        """Parse wordlist file (supports Diceware and BIP39 formats)"""
        try:
            count = 0
            temp_words = {}
            
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    
                    if len(parts) == 2 and parts[0].isdigit():
                        temp_words[parts[0]] = parts[1]
                        count += 1
                    elif len(parts) == 1 and parts[0].isalpha():
                        key = str(count + 1).zfill(4)
                        temp_words[key] = parts[0]
                        count += 1
            
            if count < 100:
                raise ValueError(f"Only found {count} words. Need at least 100.")
            
            self.wordlist = temp_words
            self.current_path = path
            self.wordlist_type, self.bits_per_word = self.detect_wordlist_type(count)
            self.loaded = True
            
            self.error_frame.pack_forget()
            self.status_label.config(
                text=f"✓ Loaded {count} words from: {path.name}", 
                fg='#10b981', font=('Segoe UI', 12, 'bold')
            )
            self.type_label.config(text=f"Type: {self.wordlist_type} ({self.bits_per_word:.1f} bits/word)")
            
            self.manual_btn.pack_forget()
            self.switch_btn.config(state=tk.NORMAL)
            
            if "BIP39" in self.wordlist_type:
                self.word_count.delete(0, tk.END)
                self.word_count.insert(0, "12")
            else:
                self.word_count.delete(0, tk.END)
                self.word_count.insert(0, "7")
            
            self.update_quantum_note()
            
            self.gen_btn.config(state=tk.NORMAL, bg=self.colors['primary'],
                              cursor='hand2', text="Generate Passphrase")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load wordlist:\n{str(e)}")
            self.show_error()
    
    def show_error(self):
        """Show error state"""
        self.error_frame.pack(fill=tk.X, pady=(0, 20), before=self.status_card)
        self.status_label.config(text=f"{self.default_filename} not found", fg='#ef4444')
        self.manual_btn.pack(pady=5)
        self.switch_btn.config(state=tk.DISABLED)
    
    def update_quantum_note(self):
        """Update quantum safety note based on current settings"""
        try:
            n = int(self.word_count.get())
        except:
            n = 6
        
        total_bits = n * self.bits_per_word if self.bits_per_word else n * 12.925
        post_quantum = total_bits / 2
        
        if post_quantum >= 128:
            status = "Post-quantum secure (256+ bits)"
            color = '#10b981'
        elif post_quantum >= 64:
            status = f"Pre-quantum secure ({total_bits:.0f} bits)"
            color = '#f59e0b'
        else:
            status = f"Weak ({total_bits:.0f} bits)"
            color = '#ef4444'
        
        self.quantum_label.config(text=f"{n} words = {total_bits:.0f} bits ({status})", fg=color)
    
    def generate(self):
        if not self.loaded:
            return
        
        try:
            n = int(self.word_count.get())
            if n < 3: n = 3
            if n > 50: n = 50
        except:
            n = 6
        
        sep = self.sep_var.get()
        words = []
        
        list_size = len(self.wordlist)
        keys = list(self.wordlist.keys())
        
        for _ in range(n):
            if "BIP39" in self.wordlist_type or list_size == 2048:
                idx = secrets.randbelow(list_size)
                word = self.wordlist[keys[idx]]
            else:
                rolls = [secrets.randbelow(6) + 1 for _ in range(5)]
                key = "".join(map(str, rolls))
                word = self.wordlist.get(key)
                if not word:
                    word = self.wordlist[keys[secrets.randbelow(list_size)]]
            
            words.append(word)
        
        passphrase = sep.join(words)
        
        # Use Text widget for multiline display
        self.pw_text.config(state='normal')
        self.pw_text.delete(1.0, tk.END)
        self.pw_text.insert(1.0, passphrase)
        self.pw_text.config(state='disabled')
        
        total_bits = n * self.bits_per_word
        combinations = int(2 ** total_bits)
        
        self.entropy_label.config(
            text=f"{n} words × {self.bits_per_word:.1f} bits = {total_bits:.1f} bits\n({combinations:,} combinations)"
        )
        
        self.output_frame.pack(fill=tk.X, padx=20, pady=10)
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def copy_to_clipboard(self):
        text = self.pw_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.copy_btn.config(text="Copied!")
        self.root.after(1500, lambda: self.copy_btn.config(text="Copy to Clipboard"))

if __name__ == "__main__":
    root = tk.Tk()
    app = DicewareApp(root)
    root.mainloop()