document.addEventListener('DOMContentLoaded', () => {
    const voiceSelect = document.getElementById('voice-select');
    const textInput = document.getElementById('text-input');
    const generateBtn = document.getElementById('generate-btn');
    const outputCard = document.getElementById('output-card');
    const audioPlayer = document.getElementById('audio-player');
    const downloadLink = document.getElementById('download-link');
    const errorMessage = document.getElementById('error-message');

    // Tab Elements
    const tabPreset = document.getElementById('tab-preset');
    const tabClone = document.getElementById('tab-clone');
    const sectionPreset = document.getElementById('section-preset');
    const sectionClone = document.getElementById('section-clone');
    const voiceFile = document.getElementById('voice-file');
    const fileCustom = document.querySelector('.file-custom');

    let currentMode = 'preset'; // 'preset' or 'clone'

    // Tab Logic
    tabPreset.addEventListener('click', () => switchTab('preset'));
    tabClone.addEventListener('click', () => switchTab('clone'));

    function switchTab(mode) {
        currentMode = mode;
        if (mode === 'preset') {
            tabPreset.classList.add('active');
            tabClone.classList.remove('active');
            sectionPreset.classList.remove('hidden');
            sectionClone.classList.add('hidden');
        } else {
            tabPreset.classList.remove('active');
            tabClone.classList.add('active');
            sectionPreset.classList.add('hidden');
            sectionClone.classList.remove('hidden');
        }
    }

    // File Input UI
    voiceFile.addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name;
        fileCustom.textContent = fileName || "Choose a WAV file...";
    });

    // Fetch voices on load
    fetchVoices();
    checkHealth();

    async function checkHealth() {
        const verSpan = document.getElementById('app-version');
        const connSpan = document.getElementById('connection-status');
        const authSpan = document.getElementById('auth-status-display');

        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                const data = await res.json();
                verSpan.textContent = `v${data.version}`;
                connSpan.textContent = "Server Online";
                connSpan.className = "status-badge success";

                authSpan.textContent = `Auth: ${data.auth_status}`;
                if (data.auth_status.includes("Logged In")) {
                    authSpan.className = "status-badge success";
                    authSpan.title = `Token: ${data.token_preview}`;
                } else {
                    authSpan.className = "status-badge error";
                }
            } else {
                throw new Error("Health check failed");
            }
        } catch (e) {
            verSpan.textContent = "v?.?.?";
            connSpan.textContent = "OFFLINE or Updating...";
            connSpan.className = "status-badge error";
            authSpan.textContent = "Auth: Unknown";
            showError("Could not connect to server. Please try restarting run.bat");
        }
    }

    async function fetchVoices() {
        try {
            const response = await fetch('/api/voices');
            if (!response.ok) throw new Error('Failed to load voices');
            const data = await response.json();

            voiceSelect.innerHTML = ''; // Clear loading option

            data.voices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.id;
                option.textContent = voice.name;
                voiceSelect.appendChild(option);
            });
        } catch (error) {
            showError('Could not load voices. Is the server running?');
            console.error(error);
        }
    }

    generateBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();

        if (!text) {
            showError('Please enter some text.');
            return;
        }

        const formData = new FormData();
        formData.append('text', text);

        if (currentMode === 'preset') {
            const voice = voiceSelect.value;
            if (!voice) {
                showError('Please select a voice.');
                return;
            }
            formData.append('voice', voice);
        } else {
            // Clone mode
            const file = voiceFile.files[0];
            if (!file) {
                showError('Please upload a voice sample.');
                return;
            }
            formData.append('file', file);
            // voice param is optional in backend if file is present
        }

        setLoading(true);
        hideError();
        outputCard.classList.add('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                // Content-Type is set automatically for FormData
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Generation failed');
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            audioPlayer.src = url;
            downloadLink.href = url;

            // Show output
            outputCard.classList.remove('hidden');
            audioPlayer.play().catch(e => console.log("Auto-play prevented:", e));

        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.classList.add('loading');
            generateBtn.disabled = true;
        } else {
            generateBtn.classList.remove('loading');
            generateBtn.disabled = false;
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    // Auth Help Logic
    const authHelpBtn = document.getElementById('auth-help-btn');
    const authHelpContent = document.getElementById('auth-help-content');

    authHelpBtn.addEventListener('click', () => {
        authHelpContent.classList.toggle('hidden');
    });

    // Detect Auth Error
    const originalShowError = showError;
    showError = function (msg) {
        originalShowError(msg);
        // Heuristic check for the specific Hugging Face auth error
        if (msg.includes("Hugging Face") || msg.includes("terms") || msg.includes("login") || msg.includes("voice cloning")) {
            if (currentMode === 'clone') {
                authHelpContent.classList.remove('hidden');
            }
        }
    };
});
