document.addEventListener('DOMContentLoaded', () => {
    const voiceSelect = document.getElementById('voice-select');
    const textInput = document.getElementById('text-input');
    const generateBtn = document.getElementById('generate-btn');
    const outputCard = document.getElementById('output-card');
    const audioPlayer = document.getElementById('audio-player');
    const downloadLink = document.getElementById('download-link');
    const errorMessage = document.getElementById('error-message');

    // Fetch voices on load
    fetchVoices();

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
        const voice = voiceSelect.value;

        if (!text) {
            showError('Please enter some text.');
            return;
        }

        if (!voice) {
            showError('Please select a voice.');
            return;
        }

        setLoading(true);
        hideError();
        outputCard.classList.add('hidden');

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, voice }),
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
});
