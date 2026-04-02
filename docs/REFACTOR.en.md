# Pentesting Analysis: Decrypt Chrome Passwords

> [!NOTE]
> **English Version** | [Versión en Español](REFACTOR.md)

> [!NOTE]
> **Historical Document** — This file describes the project's initial analysis plan. All improvements described here have been implemented in `main.py`. The referenced filename (`decrypt_chromium_passwd.py`) was renamed to `main.py` during refactoring.

This repository contains a tool designed to extract and decrypt credentials saved in Google Chrome on Windows environments. Below is a breakdown of its technical operation, along with a proposal for improvements, optimizations, and automations to elevate its level in professional security audits.

## 1. Current Operation Analysis

The script `decrypt_chromium_passwd.py` follows a logical flow of 5 critical steps to compromise the Chrome password database (versions 80+):

1. **Extraction of the "Master Key"**: Chrome encrypts passwords using a unique AES key for each installation. This key is stored encrypted in the `%LocalAppData%\Google\Chrome\User Data\Local State` file. The script extracts and decrypts it using the Windows `CryptUnprotectData` (DPAPI) API, which means it **can only be executed under the session of the user who owns the data**.
2. **Profile Identification**: It iterates over the `Default` and `Profile*` folders in the Chrome user data directory to cover all configured profiles.
3. **Database Copy**: It copies the `Login Data` file (a SQLite database) to a temporary file (`Loginvault.db`). This is crucial because if Chrome is open, the original file is locked by the browser process.
4. **AES-GCM Decryption**: It queries the `logins` table. For each entry:
    * Extracts the initialization vector (IV).
    * Uses the master key decrypted earlier to perform AES decryption in GCM mode.
5. **Results Persistence**: It generates a `decrypted_password.csv` file with the fields: Index, URL, Username, and Password.

---

## 2. Proposed Improvements and Optimizations

### A. Multi-Browser Support (Critical Level)

Currently, the script only targets Chrome. Almost all **Chromium-based** browsers use the same mechanism:

* **Microsoft Edge**: `%LocalAppData%\Microsoft\Edge\User Data\`
* **Brave-Browser**: `%LocalAppData%\BraveSoftware\Brave-Browser\User Data\`
* **Opera/Opera GX**: `%AppData%\Opera Software\Opera Stable\` (or Opera GX Stable)
* **Vivaldi**: `%LocalAppData%\Vivaldi\User Data\`

> [!TIP]
> Implementing a base class or a path dictionary would allow automating the scan of all installed browsers in a single run.

### B. Code Optimization

* **Use of `pathlib`**: Replace `os.path` and `os.environ` with `pathlib` for more modern and safer path manipulation.
* **Silent Error Handling**: In an audit, console errors can alert the user. Implement a logging system that writes to hidden files or sends errors to a remote server.
* **Total Cleanup**: The current script deletes the temporary DB file but leaves the CSV. An option for "Wipe-on-Exit" could be implemented to clear traces.

---

## 3. Pentesting and Exfiltration Capabilities

For a more effective technical audit, the following functions can be automated:

### C. Automated Exfiltration

Instead of relying on a local CSV, "Exfiltration Modules" can be added:

* **Discord/Telegram Webhook**: Send results directly to a private monitoring channel.
* **Custom HTTP/S Server**: Make a POST with the encrypted CSV content to a C2 (Command & Control).
* **Email Exfiltration**: Send the report via SMTP (less recommended due to AV/EDR detection).

### D. Stealth Mode

* **Open Browser Detection**: If Chrome is open, database copying is effective, but access to `Local State` might be detected if an aggressive EDR is present.
* **Packaging (PyInstaller)**: Convert the script into an `.exe` with all dependencies (sqlite3, pywin32, cryptodomex) integrated to make it "portable" and not require Python installed on the target.

---

## 4. Automation and Modern Reporting

### E. Premium Visual Report

Replace the CSV with an elegant and dynamic HTML report:

* Use an HTML template with in-situ searching and filtering.
* Categorize passwords by "Importance" (e.g., banks, social networks, corporate domains).

### F. Network Credential Scanning

* If domain administrator credentials are held, automate script deployment via **PsExec** or **WinRM** on multiple machines to collect passwords from an entire network in an internal audit.

---

## Summary of Pending "Upgrade" Tasks

| Improvement | Type | Impact |
| :--- | :--- | :--- |
| **Multi-Chromium** | Functional | High (Extracts more data) |
| **Remote Exfiltration** | Audit | High (Data speed) |
| **HTML UI Report** | Presentation | Medium (Professionalism) |
| **Wipe Artifacts** | Security | Medium (Anti-forensics) |
| **Portability (.exe)** | Deployment | Very High (No dependencies) |

---
