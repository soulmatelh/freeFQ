# Making your own InfusePlus IPA

This guide will walk you through creating your own InfusePlus IPA using Azule. The instructions are split into sections for **Windows (via WSL2)**, **macOS**, and **Linux**.

## 1. Setting Up Your Environment

### Windows (via WSL2)
1. **Install WSL2 (Windows Subsystem for Linux)**: WSL2 allows you to run a Linux environment directly on Windows. You will need to install **Ubuntu** or **Debian** from the Microsoft Store. Follow a tutorial such as this one to get started: [How to Install WSL2](https://www.youtube.com/watch?v=wjbbl0TTMeo).

2. **Set up Azule**: In your WSL2 terminal, follow these steps:
    ```bash
    git clone https://github.com/Al4ise/Azule ~/Azule
    sudo ln -sf ~/Azule/azule /usr/local/bin/azule
    ```

3. **Install Dependencies**: You may need additional dependencies. Run the following command in WSL2:
    ```bash
    sudo apt-get update && sudo apt install libplist-utils xmlstarlet libxml2-utils jq zip unzip zstd bzip2 -y
    ```
    Confirm that Azule is set up by typing `azule`. If it prints:
    ```bash
    [*] No Output Directory Specified. Run 'azule -h' for help
    ```
    then you're ready to proceed.

---

### macOS
1. **Install Homebrew**: If you don't have Homebrew, install it with the following command in your terminal:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Install Azule and dependencies**:
    ```bash
    git clone https://github.com/Al4ise/Azule ~/Azule
    sudo ln -sf ~/Azule/azule /usr/local/bin/azule
    ```

3. **Install dependencies**:
    ```bash
    brew install jq xmlstarlet zip unzip
    ```

4. **Verify installation**: Type `azule` in the terminal. If it prints:
    ```bash
    [*] No Output Directory Specified. Run 'azule -h' for help
    ```
    you're good to go.

---

### Linux (Debian/Ubuntu)
1. **Install Azule**: Open your terminal and run the following commands:
    ```bash
    git clone https://github.com/Al4ise/Azule ~/Azule
    sudo ln -sf ~/Azule/azule /usr/local/bin/azule
    ```

2. **Install dependencies**:
    ```bash
    sudo apt-get update && sudo apt install libplist-utils xmlstarlet libxml2-utils jq zip unzip zstd bzip2 -y
    ```

3. **Verify installation**: Run `azule` to confirm it's installed properly:
    ```bash
    [*] No Output Directory Specified. Run 'azule -h' for help
    ```

---

## 2. Obtaining the Infuse IPA and InfusePlus DEB

1. **Download the decrypted Infuse IPA**: Visit https://armconverter.com/decryptedappstore/ and search for "Infuse" and download it. You will need to sign up for an iOSGods account to access this service, which is pretty simple. Alternatively, you can use https://decrypt.day/ (no sign-up required, but may not have the latest version).

2. **Download the InfusePlus tweak file**: Get the InfusePlus tweak from the following link:
    [InfusePlus v1.2.0](https://github.com/dayanch96/InfusePlus/releases/download/v1.2.0/com.dvntm.infuseplus_1.2.0_iphoneos-arm.deb)

---

## 3. Patching the IPA with Azule

### Windows (via WSL2)
1. **Move Files to WSL2**: Place both the **Infuse.ipa** and **InfusePlus.deb** files into your WSL2 environment. You can do this by copying them into the WSL2 home folder from Windows File Explorer. This folder is usually located under `\\wsl$\Ubuntu\home\your-username`.

2. **Run the Azule patching command**:
    ```bash
    azule -i ~/Infuse.ipa -o ~/ -f ~/InfusePlus.deb -n InfusePlus -u -z
    ```
    This will create a patched **InfusePlus.ipa** in the WSL2 home directory.

---

### macOS
1. **Move Files to the Home Directory**: Place the **Infuse.ipa** and **InfusePlus.deb** files into your **~/Home** directory.

2. **Run the Azule patching command**:
    ```bash
    azule -i ~/Infuse.ipa -o ~/ -f ~/InfusePlus.deb -n InfusePlus -u -z
    ```

3. **Output**: The patched **InfusePlus.ipa** will be created in your **~/Home** folder.

---

### Linux
1. **Move Files to the Home Directory**: Make sure the **Infuse.ipa** and **InfusePlus.deb** files are located in your **~/Home** directory.

2. **Run the Azule patching command**:
    ```bash
    azule -i ~/Infuse.ipa -o ~/ -f ~/InfusePlus.deb -n InfusePlus -u -z
    ```

3. **Output**: The patched **InfusePlus.ipa** will be created in your home folder.

---

## 4. Installing the Patched IPA
Once the patched **InfusePlus.ipa** is created, you can install it on your iOS device using tools like **AltStore** or **Sideloadly**.

- [**AltStore**](https://altstore.io/): Install AltServer on your PC or Mac, then sideload the patched IPA to your iPhone or iPad.
- [**Sideloadly**](https://sideloadly.io/): Another tool for sideloading IPAs to your iOS device.

---

## Summary of the Azule Command

- `-i` is the input IPA.
- `-o` is the output directory for the patched IPA.
- `-f` is the tweak to inject (in this case, **InfusePlus.deb**).
- `-n` is the name for the output file.
- `-u` is a flag for better compatibility (removes UISupportedDevices).
- `-z` uses heavier compression to reduce IPA size.

Now you can enjoy your custom InfusePlus IPA with all the enhanced features!
