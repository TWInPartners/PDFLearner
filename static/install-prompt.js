// PWA installation prompt for Android
let deferredPrompt;
let installButton = null;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    
    // Show install button if not already shown
    if (!installButton) {
        showInstallButton();
    }
});

function showInstallButton() {
    // Create install button
    const installBtn = document.createElement('div');
    installBtn.innerHTML = `
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            z-index: 1000;
            font-family: Inter, sans-serif;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
            animation: slideInUp 0.5s ease-out;
        " onclick="installPWA()" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            📱 Install App
        </div>
        <style>
            @keyframes slideInUp {
                from {
                    transform: translateY(100px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
        </style>
    `;
    document.body.appendChild(installBtn);
    installButton = installBtn;
}

window.installPWA = async function() {
    if (deferredPrompt) {
        // Show the install prompt
        deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        // Clear the deferredPrompt variable
        deferredPrompt = null;
        // Hide the install button
        if (installButton) {
            installButton.remove();
            installButton = null;
        }
    }
};

// Listen for successful installation
window.addEventListener('appinstalled', (evt) => {
    console.log('StudyGen PWA was installed');
    if (installButton) {
        installButton.remove();
        installButton = null;
    }
});

// Check if app is already installed
if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
    console.log('App is running in standalone mode');
}