# Noiseless Measurement Configuration for ThinkPad Laptop

This README describes the steps we followed to configure our laptop for noiseless measurements, specifically for the PQDSS project. Follow the instructions below to set up and operate the system.

---

## A. Laptop Specifications
- **Model:** ThinkPad
- **Processor:** Intel Core i9 vPro (9th Gen)
- **Username:** `ubuntu`
- **Password:** `ubuntu`

---

## B. Operating System

### 1. Install Alpine Linux
- Install a lightweight Linux distribution: Alpine Linux.

### 2. Required Packages
Run the following command to install necessary packages:
```sh
apk add make cmake libssl-dev tmux git gcc openssl-dev util-linux-misc-2.39.3-r0 build-base
```

---

## C. Check Linux Distribution
To check the Linux distribution:
1. Install `lsb-release` if not already installed:
   ```sh
   apk add lsb-release
   ```
2. Verify the distribution:
   ```sh
   lsb_release -a
   ```

---

## D. Prepare Laptop for Noiseless Measurements

### 1. Isolate CPU Cores
- Edit the GRUB configuration file:
  ```sh
  sudo vim /etc/default/grub
  ```
    - Locate the line starting with `GRUB_CMDLINE_LINUX_DEFAULT`.
    - Add `isolcpus` followed by the list of CPU cores to isolate.
      Example:
      ```
      GRUB_CMDLINE_LINUX_DEFAULT="modules=sd-mod,usb-storage,ext4,nvme quiet rootfstype=ext4 isolcpus=3-15"
      ```
- Save the file and exit the editor.

### 2. Update GRUB
```sh
sudo update-grub
```

### 3. Reboot System
```sh
sudo reboot
```

### 4. Verify Isolation
- Check `/proc/cmdline` or use `taskset` to confirm CPU affinity.

### 5. Assign Task to Specific CPU
```sh
taskset --cpu-list <CPU_CORE> <COMMAND>
```

---

## E. Monitor Memory Usage

### 1. Monitor Memory Usage of a Task
```sh
export PID=<TASK_PID>
while :; do ps -p $PID -o rss=; sleep 0.1; done
```

### 2. Verify Isolated CPUs
- Check isolated CPUs:
  ```sh
  sudo vim /sys/devices/system/cpu/isolated
  ```
- Check all present CPUs:
  ```sh
  sudo vim /sys/devices/system/cpu/present
  ```

---

## F. Compiler
All candidates use gcc.

---

## G. Connect to Configured Laptop via SSH

### 1. Ensure Network Connectivity
Restart networking services:
```sh
/etc/init.d/networking restart
```

### 2. Connect to Laptop
From your personal laptop, run:
```sh
ssh -v ubuntu@10.181.84.150
```
- **Password:** `ubuntu`

### 3. Use Superuser Mode
```sh
su -
```

### 4. Use tmux for Multiple Terminals
- **Detach from current window:**
  ```
  Ctrl + B, then D
  ```
- **List windows:**
  ```
  Ctrl + B, then W
  ```

---

## H. Export Measurements to Local Computer

### 1. Create a Symbolic Link
```sh
ln -s /root/pqdss-ct-toolchain /home/ubuntu/pqdss-ct-toolchain
```

### 2. Copy Files to Non-Root Directory
```sh
cp -r /root/pqdss-ct-toolchain/ /home/ubuntu/
```

### 3. Change Ownership
```sh
chown -R ubuntu:ubuntu /home/ubuntu/pqdss-ct-toolchain/
```

### 4. Copy Files to Local Computer
From your local computer, navigate to the target directory and run:
```sh
scp -r ubuntu@10.181.84.150:/home/ubuntu/pqdss-ct-toolchain/candidates/multivariate/snova/benchmarks/snova_bench.txt .
```

---

## Notes
- Ensure the system is properly isolated and configured for accurate measurements.
- Modifying GRUB and isolating CPU cores may impact overall system performance; proceed with caution.
- For help, refer to the official documentation of the respective tools used.

---

