#!/bin/bash

# Global variables
GDRIVE_URL1="https://drive.usercontent.google.com/download?id=1-BTMZPMNv3o2_hysMmJuqave2ZOt0s5a&export=download&confirm=t"
GDRIVE_URL2="https://drive.usercontent.google.com/download?id=1-Wgj5qJ7gV5pBz7zAue7ztwcd_kKRf84&export=download&confirm=t"
GDRIVE_URL3="https://drive.usercontent.google.com/download?id=1-4q1gHdsFMVwFwjMCkZjvfwL-3cd9ZlB&export=download&confirm=t"
APK_DIR="/data/local/tmp"
APK1="$APK_DIR/capp.apk"
APK2="$APK_DIR/hma.apk"
APK3="$APK_DIR/tun2tap.apk"

# Function to download APK from Google Drive
download_apk() {
    local url="$1"
    local output="$2"
    if ! curl -L "$url" -o "$output"; then
        printf "Failed to download %s\n" "$output" >&2
        return 1
    fi
}

# Function to install APK
install_apk() {
    local apk_path="$1"
    if ! pm install "$apk_path"; then
        printf "Failed to install %s\n" "$apk_path" >&2
        return 1
    fi
}

# Main function
main() {
    # Create the directory for APKs
    mkdir -p "$APK_DIR"

    # Download and install each APK
    if ! download_apk "$GDRIVE_URL1" "$APK1"; then return 1; fi
    if ! install_apk "$APK1"; then return 1; fi

    if ! download_apk "$GDRIVE_URL2" "$APK2"; then return 1; fi
    if ! install_apk "$APK2"; then return 1; fi

    if ! download_apk "$GDRIVE_URL3" "$APK3"; then return 1; fi
    if ! install_apk "$APK3"; then return 1; fi

    printf "All APKs installed successfully.\n"
}

# Execute main function
main
