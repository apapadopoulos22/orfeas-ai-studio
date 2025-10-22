# Linux Installation Guide - Dual Boot Setup for ORFEAS Deployment

## ⚠️ IMPORTANT WARNINGS

**Before you proceed:**

- ✅ Back up all important data to external drive
- ✅ Have Windows recovery media ready
- ✅ Ensure you have 100GB+ free unallocated space
- ✅ Have Linux installation media (USB or ISO)
- ✅ Disable Fast Startup in Windows first

---

## Step 1: Back Up Your Data (CRITICAL)

### Backup Procedure

```powershell
# Connect external drive
# Copy important files to external storage:
# - Documents
# - Desktop
# - Projects
# - Database backups
# - Configuration files

# Verify backup
dir E:\backup  # (assuming E: is external drive)
```

**Use Windows Backup:**

1. Settings → System → Backup → "Backup and restore (Windows 7)"
2. Create system image on external drive
3. Create recovery USB with "Create a recovery drive"

---

## Step 2: Shrink Windows Partition (Create Free Space)

### Method 1: Using Windows Disk Management (Recommended)

1. **Open Disk Management:**

   ```powershell
   diskmgmt.msc
   ```

2. **Locate your primary partition** (usually C:)

3. **Right-click → Shrink Volume**

4. **Enter shrink size:**
   - Current size - Shrink amount
   - For 100GB free: Enter 100000 (MB) or 102400 (to be safe)

5. **Click Shrink**

6. **Verify:** You should see unallocated space of ~100GB

### Method 2: Using Command Line

```powershell
# Run as Administrator
diskpart
list disk
select disk 0  # (your main disk - verify!)
list partition
select partition C
shrink desired=102400  # Creates ~100GB unallocated space
exit
```

### Verification

```powershell
# After shrinking, you should see:
Get-Volume | Select-Object DriveLetter, Size, SizeRemaining
```

**Expected output shows C: with 100GB+ reduced size**

---

## Step 3: Disable Fast Startup

### Why This Is Important

Fast Startup can cause issues during dual-boot setup.

```powershell
# Run as Administrator
powercfg /h off  # Disable hibernation
```

**Or manually:**

1. Settings → System → Power & sleep
2. Advanced power settings
3. Disable "Fast startup"

---

## Step 4: Download Linux Installation Media

### Option A: Ubuntu 22.04 LTS (Recommended for ORFEAS)

```powershell
# Download from official source
# https://releases.ubuntu.com/22.04/

# Download:
# ubuntu-22.04.3-desktop-amd64.iso (3.3 GB)
```

**Why Ubuntu 22.04 LTS:**

- ✅ Proven with ORFEAS
- ✅ NVIDIA driver support excellent
- ✅ 5-year support (until April 2027)
- ✅ CUDA 12.1 compatible
- ✅ Docker officially supported

### Option B: Other Linux Distributions

```
Alternative Options:
├─ Ubuntu 24.04 LTS (newer, also ORFEAS-compatible)
├─ Fedora 39+ (cutting-edge, good GPU support)
└─ Debian 12 (stable, minimal)

NOT RECOMMENDED for ORFEAS:
├─ Windows Subsystem for Linux (WSL) - GPU access limited
├─ VirtualBox/VMware - GPU pass-through complex
└─ Live USB testing - Need full install for GPU drivers
```

---

## Step 5: Create Bootable USB Installation Media

### Using Rufus (Windows - Recommended)

1. **Download Rufus:**

   ```
   https://rufus.ie/
   ```

2. **Prepare USB drive:**
   - Insert 8GB+ USB drive
   - Format to FAT32 (will be overwritten anyway)

3. **Open Rufus:**
   - Device: Select your USB drive
   - Boot selection: Browse to ubuntu-22.04.3-desktop-amd64.iso
   - Partition scheme: MBR (for UEFI systems, use GPT)
   - File system: FAT32
   - Click START

4. **Wait for completion** (~5-10 minutes)

### Using PowerShell (Alternative)

```powershell
# Not recommended - Rufus is more reliable
# But if needed:

# Download ISO first
# Then use dd for Windows or similar tool
```

---

## Step 6: Boot from USB & Install Linux

### Access BIOS/UEFI Boot Menu

**Common keys by manufacturer:**

```
Manufacturer    Key(s)
─────────────────────────
ASUS            F2, Del
Dell            F2, F12
HP              F9, Esc
Lenovo          F2, F10
MSI             Del, F2
Acer            F2, Del
```

**Generic method:**

```powershell
# Restart Windows with boot menu
shutdown /r /o /t 0

# Or physically press key on boot:
# Power off → Power on → Immediately press F2/F12/Del
```

### Ubuntu Installation Steps

**1. Boot Menu Selection:**

- Select your USB drive from BIOS boot menu
- Choose "Try Ubuntu" or "Install Ubuntu"

**2. Language Selection:**

- Select "English"

**3. Keyboard Layout:**

- Select your keyboard layout (e.g., "English (US)")

**4. Software Selection:**

- Uncheck "Install third-party software" (for now)
- Continue

**5. Installation Type (CRITICAL):**

- Select "Something else" (custom partitioning)
- **DO NOT select "Erase and install"** (this will wipe Windows!)

**6. Partition Configuration:**

```
Free space (100GB unallocated) will appear as available

Create partitions:
┌─────────────────────────────────────────┐
│ Partition 1: EFI System                 │
│  Size: 512 MB                           │
│  Type: EFI System Partition             │
│  Mount: /boot/efi                       │
├─────────────────────────────────────────┤
│ Partition 2: Root Filesystem            │
│  Size: 80 GB (from 100GB free)         │
│  Type: ext4                             │
│  Mount: /                               │
├─────────────────────────────────────────┤
│ Partition 3: Home                       │
│  Size: 10 GB (remaining)               │
│  Type: ext4                             │
│  Mount: /home                           │
├─────────────────────────────────────────┤
│ Partition 4: Swap                       │
│  Size: 8 GB                             │
│  Type: Linux swap                       │
└─────────────────────────────────────────┘
```

**Steps in Ubuntu installer:**

1. Click the free space row (100GB unallocated)
2. Click "+" to add partition
3. Create each partition above
4. Set boot device to EFI partition
5. Click "Install Now"

**7. Location & Timezone:**

- Select your timezone
- Continue

**8. User Account Creation:**

```
Username: (choose a username, e.g., "orfeas")
Password: (strong password)
Computer name: (e.g., "orfeas-gpu-server")

Check: "Log in automatically" (optional)
```

**9. Installation Progress:**

- Wait for installation (15-30 minutes)
- Do NOT power off during this time

**10. Restart:**

- Remove USB drive when prompted
- System will restart into Ubuntu
- You'll see GRUB boot menu on startup

---

## Step 7: Post-Installation - First Boot

### First Login

```bash
# You'll be logged in automatically or asked for password
# Open terminal (Ctrl+Alt+T)
```

### Update System

```bash
# Update package lists
sudo apt-get update

# Upgrade packages
sudo apt-get upgrade -y

# Install essential tools
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3-pip \
    python3-venv
```

### Install NVIDIA Driver

```bash
# Add NVIDIA repository
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt-get update

# Install latest driver (handles CUDA compatibility)
sudo apt-get install -y nvidia-driver-535

# Verify installation
nvidia-smi

# Expected output:
# Driver Version: 535.x
# CUDA Version: 12.1
```

### Install NVIDIA Container Toolkit

```bash
# Add repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:12.1.0-runtime-ubuntu22.04 nvidia-smi
```

### Install Docker & Docker Compose

```bash
# Install Docker
sudo apt-get install -y docker.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker-compose --version
```

---

## Step 8: Prepare for ORFEAS Deployment

```bash
# Clone ORFEAS repository
cd /opt
sudo git clone <YOUR_REPO_URL> orfeas
cd orfeas

# Set permissions
sudo chown -R $USER:$USER /opt/orfeas

# Create directories
mkdir -p models outputs uploads temp logs
chmod 777 outputs uploads temp logs

# Verify everything
ls -la /opt/orfeas/
```

---

## Step 9: Deploy ORFEAS on Linux

```bash
# Run automated deployment
chmod +x deploy_linux.sh
./deploy_linux.sh

# Or use Docker Compose directly
docker-compose build --no-cache
docker-compose up -d

# Verify
curl http://localhost:5000/api/health
```

---

## Dual Boot Management

### Accessing Boot Menu

**On restart:**

- Power on → Press ESC, F2, or F12 (depends on BIOS)
- Select boot device:
  - Windows Boot Manager → Windows
  - Ubuntu → Linux

### From Linux to Windows

```bash
# To boot into Windows next time
# 1. Shutdown Linux
shutdown -h now

# 2. Power on and select Windows from GRUB menu
# Or select in BIOS boot priority
```

### From Windows to Linux

1. Restart Windows
2. Select Linux from GRUB menu at startup
3. Or change BIOS boot order to prioritize Linux

---

## Troubleshooting

### Issue: Can't boot into Windows

**Solution:**

```bash
# From Linux terminal
sudo os-prober  # Detect Windows
sudo grub-mkconfig -o /boot/grub/grub.cfg  # Rebuild GRUB
reboot
```

### Issue: Ubuntu doesn't boot after installation

**Solution:**

1. Boot from USB again
2. Select "Try Ubuntu"
3. Open terminal:

   ```bash
   sudo mount /dev/sdXY /mnt  # Replace X,Y with your partition
   sudo chroot /mnt
   grub-install /dev/sdX  # Replace X with your disk
   exit
   reboot
   ```

### Issue: No display after boot

**Solution:**

```bash
# Switch to TTY (Ctrl+Alt+F2)
# Login with username/password

sudo apt-get install -y ubuntu-drivers-common
ubuntu-drivers autoinstall
reboot
```

### Issue: NVIDIA driver not working

**Solution:**

```bash
# Check current driver
nvidia-smi

# If not working:
sudo apt-get purge nvidia*
sudo apt-get install -y nvidia-driver-535
sudo reboot
```

---

## Disk Space Usage

After installation, your drive will look like:

```
Total: 1TB (example)
├─ Windows: ~300GB (C: drive - intact)
├─ Linux: ~95GB
│  ├─ System: ~30GB
│  ├─ Home: ~10GB
│  ├─ Swap: ~8GB
│  └─ Free: ~47GB (for ORFEAS, models, outputs)
└─ Unallocated: 0GB
```

---

## Security Notes

- Change default GRUB timeout (optional):

  ```bash
  sudo nano /etc/default/grub
  # Change: GRUB_TIMEOUT=5
  sudo update-grub
  ```

- Set BIOS password (optional but recommended)

- Enable firewall:

  ```bash
  sudo ufw enable
  sudo ufw allow 5000/tcp  # For ORFEAS
  ```

---

## Next Steps After Linux Installation

1. ✅ Run `deploy_linux.sh` for ORFEAS deployment
2. ✅ Follow `LINUX_DEPLOYMENT_GUIDE.md`
3. ✅ Verify with health check
4. ✅ Test 3D generation

---

## Time Estimates

| Task | Time |
|------|------|
| Back up data | 30-60 min |
| Shrink Windows partition | 5-30 min |
| Download Linux ISO | 10-30 min |
| Create bootable USB | 10 min |
| Ubuntu installation | 20-40 min |
| Driver installation | 15 min |
| Docker setup | 10 min |
| ORFEAS deployment | 10-25 min |
| **TOTAL** | **2-3 hours** |

---

## Support

- Ubuntu Installation Help: https://ubuntu.com/tutorials/install-ubuntu-desktop
- NVIDIA Driver: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- Docker: https://docs.docker.com/engine/install/ubuntu/

---

**Status:** Ready to follow these steps! 🚀
