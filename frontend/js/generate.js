import { auth, BACKEND_URL } from "./firebase-config.js";
 
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const uploadZone = document.getElementById('upload-zone');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const generateForm = document.getElementById('generate-form');
    const resultsContainer = document.getElementById('results-container');
    const resultsList = document.getElementById('results-list');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message'); // ✅ Fixed: was missing
    const regenerateBtn = document.getElementById('regenerate-btn');
    const aiInsightText = document.getElementById('ai-insight-text');
    const quickLangToggles = document.getElementById('quick-lang-toggles');
 
    let selectedFile = null;
    let generatedCaptions = [];
    let currentInsight = "";
 
    // ── State Management ──────────────────────────────────────────────────────
    function saveState() {
        const state = {
            mood: document.getElementById('mood').value,
            language: document.getElementById('language').value,
            style: document.getElementById('style').value,
            previewSrc: previewImage.src,
            captions: generatedCaptions,
            insight: currentInsight,
            isPreviewVisible: !previewContainer.classList.contains('d-none'),
            isUploadHidden: uploadZone.classList.contains('d-none'),
            isResultsVisible: !resultsContainer.classList.contains('d-none')
        };
        sessionStorage.setItem('micg_generate_state', JSON.stringify(state));
    }
 
    function loadState() {
        const saved = sessionStorage.getItem('micg_generate_state');
        if (!saved) return;
        try {
            const state = JSON.parse(saved);
            document.getElementById('mood').value = state.mood || 'calm';
            document.getElementById('language').value = state.language || 'English (US)';
            document.getElementById('style').value = state.style || 'casual';
 
            if (state.previewSrc && state.previewSrc.startsWith('data:')) {
                previewImage.src = state.previewSrc;
                if (state.isPreviewVisible) previewContainer.classList.remove('d-none');
                if (state.isUploadHidden) uploadZone.classList.add('d-none');
            }
 
            if (state.captions && state.captions.length > 0) {
                generatedCaptions = state.captions;
                currentInsight = state.insight || '';
                if (aiInsightText && currentInsight) aiInsightText.textContent = currentInsight;
                renderCaptions(generatedCaptions);
                if (state.isResultsVisible) resultsContainer.classList.remove('d-none');
            }
        } catch (e) {
            console.warn('Failed to load state:', e);
            sessionStorage.removeItem('micg_generate_state');
        }
    }
 
    loadState();
 
    ['mood', 'language', 'style'].forEach(id => {
        document.getElementById(id).addEventListener('change', saveState);
    });
 
    // ── Toast ─────────────────────────────────────────────────────────────────
    function showToast(message, type = "success") {
        const toastEl = document.getElementById('toast-message');
        if (!toastEl) return;
        toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0 show`;
        const bodyEl = toastEl.querySelector('.toast-body');
        if (bodyEl) bodyEl.textContent = message;
        setTimeout(() => toastEl.classList.remove('show'), 3000);
    }
 
    // ── Drag and Drop ─────────────────────────────────────────────────────────
    if (uploadZone) {
        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('border-primary');
        });
        uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('border-primary'));
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('border-primary');
            if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files[0]);
        });
    }
 
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFiles(e.target.files[0]);
        });
    }
 
    function handleFiles(file) {
        if (!file.type.startsWith('image/')) {
            showToast("Please upload an image file.", "error");
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showToast("Image too large. Max 10MB.", "error");
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewContainer.classList.remove('d-none');
            uploadZone.classList.add('d-none');
            generatedCaptions = [];
            currentInsight = "";
            resultsList.innerHTML = '';
            resultsContainer.classList.add('d-none');
            if (aiInsightText) aiInsightText.textContent = "Analyzing visual elements...";
            saveState();
        };
        reader.readAsDataURL(file);
    }
 
    // ── Form Submission ───────────────────────────────────────────────────────
    if (generateForm) {
        generateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            performGeneration();
        });
    }
 
    if (regenerateBtn) {
        regenerateBtn.addEventListener('click', () => performGeneration());
    }
 
    async function performGeneration() {
        let fileToUpload = selectedFile;
 
        // Restore from preview if page was refreshed
        if (!fileToUpload && previewImage.src && previewImage.src.startsWith('data:')) {
            try {
                const res = await fetch(previewImage.src);
                fileToUpload = await res.blob();
            } catch (e) {
                console.warn('Could not restore image from preview:', e);
            }
        }
 
        if (!fileToUpload) {
            showToast("Please select an image first.", "error");
            return;
        }
 
        const mood = document.getElementById('mood').value;
        const language = document.getElementById('language').value;
        const style = document.getElementById('style').value;
 
        // Show loading
        loadingOverlay.classList.remove('d-none');
        if (loadingMessage) {
            loadingMessage.textContent = "Our AI is crafting unique captions... This typically takes 15-25 seconds.";
        }
 
        // Disable generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) generateBtn.disabled = true;
 
        try {
            const user = auth.currentUser;
            const idToken = user ? await user.getIdToken() : null;
 
            const formData = new FormData();
            formData.append('file', fileToUpload, 'image.jpg');
            formData.append('mood', mood);
            formData.append('language', language);
            formData.append('style', style);
 
            const headers = idToken ? { 'Authorization': `Bearer ${idToken}` } : {};
 
            const response = await fetch(`${BACKEND_URL}/generate-captions`, {
                method: 'POST',
                headers: headers,
                body: formData
            });
 
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Generation failed. Please try again.");
            }
 
            const data = await response.json();
            generatedCaptions = data.captions;
            currentInsight = data.insight;
 
            if (aiInsightText) aiInsightText.textContent = currentInsight;
            renderCaptions(generatedCaptions);
            resultsContainer.classList.remove('d-none');
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
            saveState();
 
        } catch (err) {
            console.error(err);
            showToast(err.message, "error");
        } finally {
            loadingOverlay.classList.add('d-none');
            if (generateBtn) generateBtn.disabled = false;
        }
    }
 
    // ── Render Captions ───────────────────────────────────────────────────────
    function renderCaptions(captions) {
        resultsList.innerHTML = '';
        if (!captions || captions.length === 0) {
            resultsList.innerHTML = '<p class="text-muted small text-center">No captions generated. Please try again.</p>';
            return;
        }
        captions.forEach((cap, index) => {
            const col = document.createElement('div');
            col.className = 'col-sm-6 mb-3';
            col.innerHTML = `
                <div class="glass-card p-3 h-100 d-flex flex-column caption-card">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <span class="badge bg-secondary-subtle text-muted fw-normal" style="font-size: 0.65rem;">
                            #${index + 1} • ${cap.style}
                        </span>
                    </div>
                    <p class="mb-4 text-light flex-grow-1 lead-sm">${cap.text}</p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-xs btn-outline-light action-btn copy-btn" title="Copy to clipboard">
                            <i class="bi bi-copy"></i>
                        </button>
                        <button class="btn btn-xs btn-outline-light action-btn save-caption-btn" title="Save to collection">
                            <i class="bi bi-heart"></i>
                        </button>
                        <button class="btn btn-xs btn-outline-light action-btn share-btn" title="Share caption">
                            <i class="bi bi-share"></i>
                        </button>
                    </div>
                </div>
            `;
            resultsList.appendChild(col);
            col.querySelector('.copy-btn').onclick = () => copyCaption(cap.text);
            col.querySelector('.save-caption-btn').onclick = (e) => saveCaption(e.currentTarget, cap);
            col.querySelector('.share-btn').onclick = () => shareCaption(cap.text);
        });
    }
 
    function copyCaption(text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast("Copied to clipboard!");
        }).catch(() => {
            showToast("Could not copy.", "error");
        });
    }
 
    function shareCaption(text) {
        if (navigator.share) {
            navigator.share({ title: 'AI Caption', text: text }).catch(() => copyCaption(text));
        } else {
            copyCaption(text);
        }
    }
 
    // ── Quick Language Toggles ────────────────────────────────────────────────
    if (quickLangToggles) {
        quickLangToggles.querySelectorAll('.lang-toggle').forEach(btn => {
            btn.onclick = () => {
                const lang = btn.dataset.lang;
                document.getElementById('language').value = lang;
                quickLangToggles.querySelectorAll('.lang-toggle').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (generatedCaptions.length > 0) performGeneration();
            };
        });
    }
 
    // ── Save Caption ──────────────────────────────────────────────────────────
    async function saveCaption(btn, cap) {
        try {
            const user = auth.currentUser;
            if (!user) {
                showToast("Please log in to save captions.", "error");
                return;
            }
            const idToken = await user.getIdToken();
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
 
            const response = await fetch(`${BACKEND_URL}/captions/save`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${idToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: cap.text,
                    mood: cap.mood,
                    language: cap.language,
                    style: cap.style
                })
            });
 
            if (!response.ok) throw new Error("Failed to save.");
            btn.innerHTML = '<i class="bi bi-heart-fill text-danger"></i>';
            showToast("Caption saved!");
        } catch (err) {
            console.error(err);
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-heart"></i>';
            showToast("Could not save.", "error");
        }
    }
});
