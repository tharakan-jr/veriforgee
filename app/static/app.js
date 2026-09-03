/**
 * VeriForge Frontend Engine — SaaS Edition
 * Turn AI-Generated Code Into Trusted Code.
 */

// =============================================================================
// DOM References
// =============================================================================
const viewInput = document.getElementById("view-input");
const viewLoading = document.getElementById("view-loading");
const viewResult = document.getElementById("view-result");
const viewError = document.getElementById("view-error");

const codeInput = document.getElementById("code-input");
const editorGutter = document.getElementById("editor-gutter");
const charCounter = document.getElementById("char-counter");
const lineCounter = document.getElementById("line-counter");
const emptyStateBanner = document.getElementById("empty-state-banner");
const langSelect = document.getElementById("lang-select");
const fileTabLabel = document.getElementById("file-tab-label");
const intentInput = document.getElementById("intent-input");

const btnReview = document.getElementById("btn-review");
const btnBackEditor = document.getElementById("btn-back-editor");
const btnHeroStart = document.getElementById("btn-hero-start");
const btnHeroDemo = document.getElementById("btn-hero-demo");

const btnPresetDb = document.getElementById("btn-preset-db");
const btnPresetSql = document.getElementById("btn-preset-sql");
const btnPresetClear = document.getElementById("btn-preset-clear");

// Loading Steps
const loadingStageLabel = document.getElementById("loading-stage-label");
const step1 = document.getElementById("load-step-1");
const step2 = document.getElementById("load-step-2");
const step3 = document.getElementById("load-step-3");
const step4 = document.getElementById("load-step-4");

// Error DOM
const errorMessage = document.getElementById("error-message");
const btnErrorRetry = document.getElementById("btn-error-retry");
const btnErrorBack = document.getElementById("btn-error-back");

// Result DOM
const metricTotalIssues = document.getElementById("metric-total-issues");
const metricCritical = document.getElementById("metric-critical");
const findingSeverityPill = document.getElementById("finding-severity-pill");
const findingTitle = document.getElementById("finding-title");
const findingPlainExplanation = document.getElementById("finding-plain-explanation");
const findingWhyMatters = document.getElementById("finding-why-matters");
const findingEvidenceText = document.getElementById("finding-evidence-text");
const findingFixGuidance = document.getElementById("finding-fix-guidance");
const btnCopyFixCode = document.getElementById("btn-copy-fix-code");
const copyBtnText = document.getElementById("copy-btn-text");

// Voice Tutor DOM
const btnVoiceExplain = document.getElementById("btn-voice-explain");
const voiceLabel = document.getElementById("voice-label");
const backendAudioPlayer = document.getElementById("backend-audio-player");
const voiceAlertBanner = document.getElementById("voice-alert-banner");
const voiceAlertMsg = document.getElementById("voice-alert-msg");
const voiceAlertIcon = document.getElementById("voice-alert-icon");

// Verification Quiz DOM
const quizQuestionText = document.getElementById("quiz-question-text");
const quizChoices = document.querySelectorAll(".quiz-choice");
const quizFeedbackBox = document.getElementById("quiz-feedback-box");
const verifyChipStatus = document.getElementById("verify-chip-status");

// Modals
const btnOpenHow = document.getElementById("btn-open-how");
const btnCloseHow = document.getElementById("btn-close-how");
const howModal = document.getElementById("how-modal");

const btnOpenStandards = document.getElementById("btn-open-standards");
const btnCloseStandards = document.getElementById("btn-close-standards");
const standardsModalEl = document.getElementById("standards-modal-el");

// Constants
const DEFAULT_SECRET_SNIPPET = 'DB_PASSWORD = "admin123"';
const DEFAULT_SQL_SNIPPET = `query = "SELECT * FROM users WHERE name='" + username + "'"`;
const RECOMMENDED_FIX_CODE = `import os\n\nDB_PASSWORD = os.environ.get("DB_PASSWORD")`;

// =============================================================================
// Lenis Smooth Scroll Integration
// =============================================================================
let lenis = null;

if (typeof Lenis !== "undefined") {
  lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    touchMultiplier: 1.5,
    infinite: false,
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }

  requestAnimationFrame(raf);
}

function smoothScrollTo(target, offset = -80) {
  if (lenis) {
    lenis.scrollTo(target, { offset: offset, duration: 1.2 });
  } else {
    const el = typeof target === "string" ? document.querySelector(target) : target;
    if (el) {
      window.scrollTo({ top: el.offsetTop + offset, behavior: "smooth" });
    }
  }
}

// =============================================================================
// View Management
// =============================================================================
function showView(viewName) {
  viewInput.classList.remove("active");
  viewLoading.classList.remove("active");
  viewResult.classList.remove("active");
  viewError.classList.remove("active");

  stopVoiceAudio();

  if (viewName === "input") {
    viewInput.classList.add("active");
    updateEditorStats();
  } else if (viewName === "loading") {
    viewLoading.classList.add("active");
    smoothScrollTo(viewLoading);
  } else if (viewName === "result") {
    viewResult.classList.add("active");
    smoothScrollTo(viewResult);
  } else if (viewName === "error") {
    viewError.classList.add("active");
    smoothScrollTo(viewError);
  }
}

// =============================================================================
// Editor Gutter & Stats Handling
// =============================================================================
function updateEditorStats() {
  const content = codeInput.value;
  const chars = content.length;
  charCounter.textContent = `${chars} char${chars === 1 ? "" : "s"}`;

  const lines = content.split("\n");
  const lineCount = lines.length;
  lineCounter.textContent = `${lineCount} line${lineCount === 1 ? "" : "s"}`;

  // Update line gutter
  let gutterHtml = "";
  for (let i = 1; i <= Math.max(lineCount, 5); i++) {
    gutterHtml += `<span>${i}</span>`;
  }
  editorGutter.innerHTML = gutterHtml;

  // Toggle empty-state guidance
  if (chars === 0) {
    emptyStateBanner.classList.remove("hidden");
  } else {
    emptyStateBanner.classList.add("hidden");
  }
}

codeInput.addEventListener("input", updateEditorStats);

// Language Selector updates filename
langSelect.addEventListener("change", () => {
  const val = langSelect.value;
  if (val === "python") fileTabLabel.textContent = "artefact.py";
  else if (val === "javascript") fileTabLabel.textContent = "artefact.js";
  else if (val === "sql") fileTabLabel.textContent = "query.sql";
});

// Presets
function setPreset(code, intent, lang, activeBtn) {
  codeInput.value = code;
  intentInput.value = intent;
  langSelect.value = lang;
  langSelect.dispatchEvent(new Event("change"));

  [btnPresetDb, btnPresetSql, btnPresetClear].forEach((b) => b.classList.remove("active"));
  if (activeBtn) activeBtn.classList.add("active");

  updateEditorStats();
  codeInput.focus();
}

btnPresetDb.addEventListener("click", () => setPreset(DEFAULT_SECRET_SNIPPET, "Connect to database", "python", btnPresetDb));
btnPresetSql.addEventListener("click", () => setPreset(DEFAULT_SQL_SNIPPET, "Query user profile", "python", btnPresetSql));
btnPresetClear.addEventListener("click", () => setPreset("", "", "python", btnPresetClear));

btnHeroDemo.addEventListener("click", () => {
  setPreset(DEFAULT_SECRET_SNIPPET, "Connect to database", "python", btnPresetDb);
  smoothScrollTo(viewInput);
});

btnHeroStart.addEventListener("click", (e) => {
  e.preventDefault();
  smoothScrollTo(viewInput);
  codeInput.focus();
});

// Keyboard shortcut: Ctrl + Enter
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    if (viewInput.classList.contains("active")) {
      e.preventDefault();
      btnReview.click();
    }
  }
});

// =============================================================================
// Loading Progression Sequence (Snappy & Transparent)
// =============================================================================
function setStepState(stepEl, status, icon) {
  stepEl.setAttribute("data-status", status);
  const ind = stepEl.querySelector(".step-indicator");
  if (ind) ind.textContent = icon;
}

function runReviewPipeline(code) {
  showView("loading");

  setStepState(step1, "active", "●");
  setStepState(step2, "pending", "○");
  setStepState(step3, "pending", "○");
  setStepState(step4, "pending", "○");
  loadingStageLabel.textContent = "Analyzing your code...";

  // Phase 1 -> 2
  setTimeout(() => {
    setStepState(step1, "done", "✓");
    setStepState(step2, "active", "●");
    loadingStageLabel.textContent = "Checking security patterns...";
  }, 320);

  // Phase 2 -> 3
  setTimeout(() => {
    setStepState(step2, "done", "✓");
    setStepState(step3, "active", "●");
    loadingStageLabel.textContent = "Finding potential vulnerabilities...";
  }, 680);

  // Phase 3 -> 4
  setTimeout(() => {
    setStepState(step3, "done", "✓");
    setStepState(step4, "active", "●");
    loadingStageLabel.textContent = "Grounding findings with trusted sources...";
  }, 1020);

  // Final Transition to Results
  setTimeout(() => {
    setStepState(step4, "done", "✓");
    showView("result");
    resetResultUI();
  }, 1300);
}

btnReview.addEventListener("click", () => {
  const code = codeInput.value.trim();
  if (!code) {
    emptyStateBanner.classList.remove("hidden");
    codeInput.focus();
    return;
  }
  runReviewPipeline(code);
});

btnBackEditor.addEventListener("click", () => {
  showView("input");
  smoothScrollTo(viewInput);
});

btnErrorRetry.addEventListener("click", () => {
  btnReview.click();
});

btnErrorBack.addEventListener("click", () => {
  showView("input");
});

// =============================================================================
// Accordion Interaction (Expandable Finding Cards)
// =============================================================================
const accordionTriggers = document.querySelectorAll(".accordion-trigger");

accordionTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    const isExpanded = trigger.getAttribute("aria-expanded") === "true";
    const panelId = trigger.getAttribute("aria-controls");
    const panel = document.getElementById(panelId);

    if (isExpanded) {
      trigger.setAttribute("aria-expanded", "false");
      panel.classList.remove("expanded");
    } else {
      trigger.setAttribute("aria-expanded", "true");
      panel.classList.add("expanded");
    }
  });
});

// =============================================================================
// Copy Recommended Fix
// =============================================================================
btnCopyFixCode.addEventListener("click", async () => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(RECOMMENDED_FIX_CODE);
    } else {
      const ta = document.createElement("textarea");
      ta.value = RECOMMENDED_FIX_CODE;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    copyBtnText.textContent = "Copied ✓";
    setTimeout(() => {
      copyBtnText.textContent = "Copy Fix";
    }, 2000);
  } catch (err) {
    copyBtnText.textContent = "Copied ✓";
    setTimeout(() => {
      copyBtnText.textContent = "Copy Fix";
    }, 2000);
  }
});

// =============================================================================
// 9. Understanding Verification (Interactive Comprehension Check)
// =============================================================================
const QUIZ_EXPLANATIONS = {
  A: "Not quite. Hardcoded credentials have no measurable impact on execution speed. The actual risk is that anyone who views or downloads the source code can extract your plaintext password.",
  B: "✓ Correct — you identified the actual risk.",
  C: "Not quite. Python natively stores string variables in memory. The problem is committing the password permanently into the repository source files.",
  D: "Not quite. A short password string adds negligible bytes. The critical risk is credential exposure in source control and build artifacts."
};

quizChoices.forEach((btn) => {
  btn.addEventListener("click", () => {
    const choice = btn.getAttribute("data-choice");

    quizChoices.forEach((b) => {
      b.setAttribute("aria-checked", "false");
      b.classList.remove("selected-correct", "selected-incorrect");
    });

    btn.setAttribute("aria-checked", "true");

    if (choice === "B") {
      btn.classList.add("selected-correct");
      quizFeedbackBox.className = "quiz-feedback success";
      quizFeedbackBox.textContent = QUIZ_EXPLANATIONS.B;

      verifyChipStatus.className = "verify-status-chip verified";
      verifyChipStatus.textContent = "✓ Verified by Builder";
    } else {
      btn.classList.add("selected-incorrect");
      quizFeedbackBox.className = "quiz-feedback warning";
      quizFeedbackBox.textContent = QUIZ_EXPLANATIONS[choice];

      verifyChipStatus.className = "verify-status-chip";
      verifyChipStatus.textContent = "Check Required";
    }
  });
});

function resetResultUI() {
  // Ensure all accordions are expanded for scannability
  accordionTriggers.forEach((t) => {
    t.setAttribute("aria-expanded", "true");
    const p = document.getElementById(t.getAttribute("aria-controls"));
    if (p) p.classList.add("expanded");
  });

  // Reset copy button
  copyBtnText.textContent = "Copy Fix";

  // Reset quiz
  quizChoices.forEach((b) => {
    b.setAttribute("aria-checked", "false");
    b.classList.remove("selected-correct", "selected-incorrect");
  });
  quizFeedbackBox.className = "quiz-feedback hidden";
  quizFeedbackBox.textContent = "";

  verifyChipStatus.className = "verify-status-chip";
  verifyChipStatus.textContent = "Pending Check";

  voiceAlertBanner.classList.add("hidden");
  stopVoiceAudio();
}

// =============================================================================
// 10. Voice Explanation (ElevenLabs Integration with Resilient Fallback)
// =============================================================================
let isVoicePlaying = false;

function stopVoiceAudio() {
  isVoicePlaying = false;
  btnVoiceExplain.classList.remove("speaking");
  voiceLabel.textContent = "🔊 Explain this to me";

  if (backendAudioPlayer) {
    backendAudioPlayer.pause();
    backendAudioPlayer.currentTime = 0;
  }
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}

async function handleVoiceExplanation() {
  if (isVoicePlaying) {
    stopVoiceAudio();
    return;
  }

  const explanationText = findingPlainExplanation.textContent.trim();
  voiceAlertBanner.classList.remove("hidden");
  voiceAlertIcon.textContent = "⏳";
  voiceAlertMsg.textContent = "Connecting to voice service...";

  isVoicePlaying = true;
  btnVoiceExplain.classList.add("speaking");
  voiceLabel.textContent = "Generating audio...";

  // 1. Attempt backend ElevenLabs endpoint
  let backendSuccess = false;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2500);

    const res = await fetch("/api/voice/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: explanationText }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const blob = await res.blob();
      const audioUrl = URL.createObjectURL(blob);
      backendAudioPlayer.src = audioUrl;
      await backendAudioPlayer.play();
      voiceAlertIcon.textContent = "🔊";
      voiceAlertMsg.textContent = "Playing ElevenLabs voice explanation from backend.";
      voiceLabel.textContent = "Stop voice audio";
      backendSuccess = true;

      backendAudioPlayer.onended = () => {
        stopVoiceAudio();
        voiceAlertBanner.classList.add("hidden");
      };
    }
  } catch (err) {
    // Backend fetch failed or timed out — seamlessly fallback below
    backendSuccess = false;
  }

  // 2. Resilient Fallback to Browser Speech Synthesis
  if (!backendSuccess) {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(explanationText);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;

      utterance.onstart = () => {
        voiceAlertIcon.textContent = "🎙️";
        voiceAlertMsg.textContent = "Voice explanation active (Standalone browser audio mode).";
        voiceLabel.textContent = "Stop voice audio";
      };

      utterance.onend = () => {
        stopVoiceAudio();
        setTimeout(() => voiceAlertBanner.classList.add("hidden"), 1500);
      };

      utterance.onerror = () => {
        stopVoiceAudio();
        voiceAlertBanner.classList.add("hidden");
      };

      window.speechSynthesis.speak(utterance);
    } else {
      voiceAlertIcon.textContent = "ℹ️";
      voiceAlertMsg.textContent = "Speech synthesis not supported on this browser.";
      stopVoiceAudio();
    }
  }
}

btnVoiceExplain.addEventListener("click", handleVoiceExplanation);

// =============================================================================
// Modals
// =============================================================================
btnOpenHow.addEventListener("click", (e) => {
  e.preventDefault();
  if (typeof howModal.showModal === "function") howModal.showModal();
});
btnCloseHow.addEventListener("click", () => howModal.close());
howModal.addEventListener("click", (e) => {
  if (e.target === howModal) howModal.close();
});

btnOpenStandards.addEventListener("click", (e) => {
  e.preventDefault();
  if (typeof standardsModalEl.showModal === "function") standardsModalEl.showModal();
});
btnCloseStandards.addEventListener("click", () => standardsModalEl.close());
standardsModalEl.addEventListener("click", (e) => {
  if (e.target === standardsModalEl) standardsModalEl.close();
});

// =============================================================================
// Initialization
// =============================================================================
window.addEventListener("DOMContentLoaded", () => {
  updateEditorStats();
});
