# 🔐 Secure Password Generator

**Diceware • BIP39 • Post-Quantum Ready**

[![Python](https://img.shields.io/badge/python-3.6+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-10b981?style=flat-square)](LICENSE)
[![Size](https://img.shields.io/badge/size-&lt;15KB-f43f5e?style=flat-square)](#)
[![Dependencies](https://img.shields.io/badge/dependencies-0-8b5cf6?style=flat-square)](#)

*Cryptographically secure passphrases. Offline. Auditable.*

[📥 Download Latest](password_generator.py)

---

## ✨ Why This Generator?

| 🚫 The Problem | ✅ Our Solution |
|:---|:---|
| **Cloud Leaks** — Online generators transmit passwords to servers | **100% Offline** — Never connects to internet. Air-gappable. |
| **Hidden Code** — EXEs/apps could contain backdoors or telemetry | **Open Source** — 200 lines of readable Python. Verify every byte. |
| **Weak Randomness** — Browser Math.random() or time-based seeds | **True Crypto RNG** — Uses OS entropy pool (CSPRNG) |
| **Quantum Future** — 12-word passwords broken by tomorrow's computers | **Post-Quantum** — Supports 24-word BIP39 (264 bits) |

---

## 🛡️ Security Features

### 🔒 Memory Safe
Passwords exist **only in RAM**. No temp files, no logs, no history.

- ✅ Zero disk writes
- ✅ No clipboard history (unless OS saves it)
- ✅ Process memory cleared on exit
- ✅ Works in Tails OS / RAM disks

### 🎲 True Randomness
Uses Python's `secrets` module (accesses `/dev/urandom`, CryptGenRandom, etc.)

- ✅ Not pseudo-random
- ✅ Not seedable/predictable
- ✅ Side-channel resistant

### 🧮 Quantum Resistance
Generate passwords that survive Grover's algorithm.

- ✅ 24 words = 264 bits (post-quantum secure)
- ✅ Auto-calculates entropy
- ✅ BIP39 crypto wallet compatible

---

## 📜 License

MIT License — Free for personal and commercial use. No warranty provided.

**⚠️ Cryptographic Notice:** This tool generates randomness using your operating system's CSPRNG. It is suitable for passwords and crypto seed phrases. However, if your OS or hardware RNG is compromised, this tool cannot help. For life-critical keys, use multiple independent generation methods and XOR them together.
## 🚀 Installation

### Windows 10/11
```powershell
# 1. Install Python from Microsoft Store or python.org
# 2. Verify Tkinter is included:
python -c "import tkinter; print('OK')"

# 3. Run
python password_generator.py
