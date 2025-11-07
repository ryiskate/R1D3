# Self-Hosted Git Server Setup Guide

This guide will help you set up your own Git server with LFS support for the R1D3 project.

## Why Self-Host?

- ✅ **Unlimited storage** - No monthly fees for large files
- ✅ **Complete control** - Your data, your rules
- ✅ **Learning experience** - Understand Git infrastructure
- ✅ **Privacy** - Keep everything on your own hardware
- ✅ **Cost-effective** - One-time setup vs monthly subscriptions

---

## Option 1: Gitea (Recommended for Beginners)

**Gitea** is a lightweight, self-hosted Git service written in Go. It's easy to set up and has a GitHub-like interface.

### Requirements
- A computer/server that stays online (can be a home PC, Raspberry Pi, or VPS)
- Windows, Linux, or macOS
- At least 512MB RAM
- Storage space for your repositories

### Installation Steps

#### On Windows:

1. **Download Gitea**
   ```powershell
   # Download from https://gitea.io/en-us/
   # Or use this direct link for Windows:
   Invoke-WebRequest -Uri "https://dl.gitea.com/gitea/latest/gitea-latest-windows-4.0-amd64.exe" -OutFile "gitea.exe"
   ```

2. **Create a directory for Gitea**
   ```powershell
   mkdir C:\gitea
   cd C:\gitea
   # Move gitea.exe here
   ```

3. **Run Gitea**
   ```powershell
   .\gitea.exe web
   ```

4. **Access the web interface**
   - Open browser: `http://localhost:3000`
   - Complete the installation wizard
   - Choose SQLite as database (simplest)
   - Set admin username and password

5. **Install as Windows Service** (optional, for auto-start)
   ```powershell
   # Run as Administrator
   sc.exe create gitea start= auto binPath= "C:\gitea\gitea.exe web --config C:\gitea\custom\conf\app.ini"
   ```

#### On Linux (Ubuntu/Debian):

```bash
# Download Gitea
wget -O /usr/local/bin/gitea https://dl.gitea.com/gitea/latest/gitea-latest-linux-amd64
chmod +x /usr/local/bin/gitea

# Create gitea user
sudo adduser --system --shell /bin/bash --gecos 'Git Version Control' --group --disabled-password --home /home/git git

# Create directories
sudo mkdir -p /var/lib/gitea/{custom,data,log}
sudo chown -R git:git /var/lib/gitea/
sudo chmod -R 750 /var/lib/gitea/

# Create systemd service
sudo nano /etc/systemd/system/gitea.service
```

**Paste this into gitea.service:**
```ini
[Unit]
Description=Gitea (Git with a cup of tea)
After=syslog.target
After=network.target

[Service]
RestartSec=2s
Type=simple
User=git
Group=git
WorkingDirectory=/var/lib/gitea/
ExecStart=/usr/local/bin/gitea web --config /etc/gitea/app.ini
Restart=always
Environment=USER=git HOME=/home/git GITEA_WORK_DIR=/var/lib/gitea

[Install]
WantedBy=multi-user.target
```

```bash
# Start Gitea
sudo systemctl enable gitea
sudo systemctl start gitea

# Access at http://localhost:3000
```

### Configure Git LFS in Gitea

1. Edit `app.ini` (location varies by OS)
   - Windows: `C:\gitea\custom\conf\app.ini`
   - Linux: `/etc/gitea/app.ini`

2. Add LFS configuration:
   ```ini
   [server]
   LFS_START_SERVER = true
   LFS_JWT_SECRET = <generate-a-secret-key>
   
   [lfs]
   PATH = /var/lib/gitea/data/lfs  # Or C:\gitea\data\lfs on Windows
   ```

3. Restart Gitea

### Access from Outside Your Network

**Option A: Port Forwarding (Home Network)**
1. Forward port 3000 on your router to your Gitea server
2. Get your public IP: `curl ifconfig.me`
3. Access via: `http://YOUR_PUBLIC_IP:3000`
4. **Security:** Use strong passwords, enable 2FA

**Option B: Cloudflare Tunnel (Recommended - Free & Secure)**
```bash
# Install cloudflared
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create r1d3-git

# Configure tunnel
cloudflared tunnel route dns r1d3-git git.yourdomain.com

# Run tunnel
cloudflared tunnel run r1d3-git
```

**Option C: Tailscale (VPN - Easiest)**
```bash
# Install Tailscale on both computers
# Access Gitea via Tailscale IP (e.g., 100.x.x.x:3000)
# No port forwarding needed!
```

---

## Option 2: GitLab CE (Feature-Rich)

**GitLab Community Edition** is more powerful but requires more resources.

### Requirements
- 4GB RAM minimum (8GB recommended)
- 2 CPU cores
- 10GB storage + repository space

### Installation (Linux)

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl

# Add GitLab repository
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# Install GitLab
sudo EXTERNAL_URL="http://git.yourdomain.com" apt-get install gitlab-ce

# Configure LFS (already enabled by default)
sudo gitlab-ctl reconfigure
```

### Access
- Default URL: `http://localhost`
- Get root password: `sudo cat /etc/gitlab/initial_root_password`

---

## Option 3: Simple Git Server (Minimal)

For the absolute minimal setup (no web interface):

### On Linux:

```bash
# Install git
sudo apt-get install git

# Create git user
sudo adduser git

# Setup SSH keys
su - git
mkdir .ssh && chmod 700 .ssh
touch .ssh/authorized_keys && chmod 600 .ssh/authorized_keys

# Add your public SSH key to authorized_keys

# Create repository
mkdir /home/git/r1d3.git
cd /home/git/r1d3.git
git init --bare

# Install git-lfs
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
```

### On your local machine:

```bash
# Add remote
git remote add selfhosted git@YOUR_SERVER_IP:/home/git/r1d3.git

# Push
git push selfhosted master
```

---

## Migrating from GitHub to Self-Hosted

When you're ready to switch:

```bash
# Add your self-hosted server as a remote
git remote add selfhosted http://your-gitea-server:3000/username/R1D3.git

# Push everything (including LFS)
git push selfhosted --all
git lfs push selfhosted --all

# Optional: Change origin
git remote rename origin github
git remote rename selfhosted origin
```

---

## Backup Strategy

**Important:** Always backup your Git server!

### Automated Backup Script (Linux)

```bash
#!/bin/bash
# backup-gitea.sh

BACKUP_DIR="/backup/gitea"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Gitea data
tar -czf "$BACKUP_DIR/gitea-data-$DATE.tar.gz" /var/lib/gitea/data
tar -czf "$BACKUP_DIR/gitea-repos-$DATE.tar.gz" /var/lib/gitea/repositories

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

# Optional: Sync to cloud
rclone copy $BACKUP_DIR remote:gitea-backups
```

### Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /home/git/backup-gitea.sh
```

---

## Cost Comparison

### GitHub with LFS
- Free: 1GB storage, 1GB bandwidth/month
- Pro ($4/mo): 50GB storage, 50GB bandwidth
- Team ($4/user/mo): 50GB storage, 50GB bandwidth

### Self-Hosted (One-Time Costs)
- **Raspberry Pi 4 (4GB)**: ~$75 (perfect for Gitea)
- **Old PC**: $0 (reuse existing hardware)
- **VPS**: $5-10/month (DigitalOcean, Linode, Hetzner)
- **Electricity**: ~$2-5/month (Raspberry Pi)

**Break-even point:** 2-3 months vs GitHub Pro

---

## Recommended Setup for R1D3

**Phase 1 (Now):** GitHub + Git LFS (free tier)
- Learn Git LFS workflow
- See how much storage you actually need

**Phase 2 (Later):** Self-hosted Gitea
- **Hardware:** Raspberry Pi 4 (4GB) or old laptop
- **Software:** Gitea + Git LFS
- **Access:** Tailscale VPN (easiest) or Cloudflare Tunnel (most secure)
- **Backup:** Daily automated backups to external drive + cloud

**Phase 3 (Future):** Scale as needed
- Upgrade to more powerful hardware if needed
- Add CI/CD with Gitea Actions
- Set up automated testing

---

## Security Best Practices

1. **Use SSH keys** instead of passwords
2. **Enable 2FA** on admin accounts
3. **Regular updates** - Keep Gitea/GitLab updated
4. **Firewall** - Only expose necessary ports
5. **HTTPS** - Use Let's Encrypt for free SSL certificates
6. **Backups** - Automate and test regularly
7. **Monitoring** - Set up uptime monitoring

---

## Troubleshooting

### Git LFS not working?
```bash
# Verify LFS is installed
git lfs version

# Re-initialize LFS
git lfs install --force

# Check tracked files
git lfs ls-files
```

### Can't push large files?
```bash
# Increase Git buffer size
git config --global http.postBuffer 524288000

# Or use SSH instead of HTTPS
git remote set-url origin git@your-server:username/repo.git
```

### Gitea won't start?
```bash
# Check logs
sudo journalctl -u gitea -n 50

# Check if port 3000 is already in use
sudo netstat -tulpn | grep 3000
```

---

## Next Steps

1. ✅ **Current:** Using GitHub + Git LFS
2. 📝 **Plan:** Decide on hardware (Raspberry Pi vs old PC vs VPS)
3. 🧪 **Test:** Set up Gitea locally to experiment
4. 🚀 **Deploy:** Move to self-hosted when comfortable
5. 🔄 **Maintain:** Set up backups and monitoring

---

## Resources

- **Gitea Documentation:** https://docs.gitea.io/
- **GitLab Documentation:** https://docs.gitlab.com/
- **Git LFS Tutorial:** https://github.com/git-lfs/git-lfs/wiki/Tutorial
- **Tailscale Setup:** https://tailscale.com/kb/
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/

---

**Remember:** Start simple, learn as you go, and scale when needed. The experience of running your own Git server is invaluable! 🚀
