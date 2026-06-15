# Cursor Remote-SSH to PPE loop VM

**Purpose:** run Cursor Agent **on the VM** (`desktop-caqll8k`) from your daily PC — no Hyper-V copy/paste.

**Prerequisite:** OpenSSH + Tailscale on VM — see [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md).

---

## One-time setup (host PC)

### 1. SSH works

```powershell
ssh ppeloop@desktop-caqll8k
```

Password: VM user password. Type `yes` on first connect. `exit` to leave.

### 2. SSH config

**Ctrl+Shift+P** → **Remote-SSH: Open SSH Configuration File** →  
`C:\Users\USER\.ssh\config`

```
Host ppe-vm
    HostName desktop-caqll8k
    User ppeloop
```

Save.

### 3. Cursor extension

Extensions → **Remote - SSH** (Microsoft) → Install.

### 4. Connect

**Ctrl+Shift+P** → **Remote-SSH: Connect to Host…** → **ppe-vm**  
Password when prompted.

### 5. Open repo

**File → Open Folder** →  
`C:\Users\ppeloop\Probability-prediction-engine`

Bottom-left should show **SSH: ppe-vm**. Agent chat in **this** window runs on the VM.

---

## Daily use

| Task | Where |
|------|--------|
| Product code, PRs | **Host** Cursor (default) |
| VM stack, ntfy, operator fixes | **Remote-SSH** `ppe-vm` window |
| Quick status | `ssh ppeloop@desktop-caqll8k` → `.\ppe_autobuilder.cmd status --brief` |

---

## Optional: SSH key (no password each time)

On **host** PowerShell:

```powershell
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ppe_vm -N '""'
type $env:USERPROFILE\.ssh\id_ppe_vm.pub | ssh ppeloop@desktop-caqll8k "mkdir .ssh 2>nul & type >> .ssh\authorized_keys"
```

Add to `config`:

```
Host ppe-vm
    HostName desktop-caqll8k
    User ppeloop
    IdentityFile ~/.ssh/id_ppe_vm
```
