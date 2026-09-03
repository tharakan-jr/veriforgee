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

// Dynamic Snippet & Grounding DOM
const findingSnippetContent = document.getElementById("finding-snippet-content");
const findingCwePill = document.getElementById("finding-cwe-pill");
const pipeFindingVal = document.getElementById("pipe-finding-val");
const pipeRuleVal = document.getElementById("pipe-rule-val");
const pipeEvidenceVal = document.getElementById("pipe-evidence-val");
const findingSourcePill = document.getElementById("finding-source-pill");
const findingSourceRef = document.getElementById("finding-source-ref");
const findingApplicabilityText = document.getElementById("finding-applicability-text");

// Diff & Fix Verification DOM
const diffBeforeCode = document.getElementById("diff-before-code");
const diffAfterCode = document.getElementById("diff-after-code");
const diffBeforeTag = document.getElementById("diff-before-tag");
const diffAfterTag = document.getElementById("diff-after-tag");
const btnRunVerifyFix = document.getElementById("btn-run-verify-fix");
const fixVerifyResultBox = document.getElementById("fix-verify-result-box");
const fixVerifyBadge = document.getElementById("fix-verify-badge");

// Voice Tutor DOM
const btnVoiceExplain = document.getElementById("btn-voice-explain");
const voiceLabel = document.getElementById("voice-label");
const backendAudioPlayer = document.getElementById("backend-audio-player");
const voiceAlertBanner = document.getElementById("voice-alert-banner");
const voiceAlertMsg = document.getElementById("voice-alert-msg");
const voiceAlertIcon = document.getElementById("voice-alert-icon");

// Verification Quiz DOM
const quizQuestionText = document.getElementById("quiz-question-text");
const quizChoicesContainer = document.getElementById("quiz-choices-container");
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

// Application State
let currentOriginalCode = "";
let currentFinding = null;
let currentFixedCode = "";
let voiceConfigured = false;

// =============================================================================
// Helper Utilities
// =============================================================================
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

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

function smoothScrollTo(target) {
  if (lenis && target) {
    lenis.scrollTo(target, { offset: -30, duration: 1.1 });
  } else if (target) {
    target.scrollIntoView({ behavior: "smooth" });
  }
}

// =============================================================================
// Editor Line Numbering & Counter Synchronization
// =============================================================================
function updateEditorStats() {
  const text = codeInput.value;
  const lines = text.split("\n");
  const lineCount = lines.length || 1;
  const charCount = text.length;

  charCounter.textContent = `${charCount.toLocaleString()} chars`;
  lineCounter.textContent = `${lineCount.toLocaleString()} lines`;

  let gutterHtml = "";
  for (let i = 1; i <= lineCount; i++) {
    gutterHtml += `<span>${i}</span>`;
  }
  editorGutter.innerHTML = gutterHtml;
}

codeInput.addEventListener("input", () => {
  updateEditorStats();
  if (codeInput.value.trim().length > 0) {
    emptyStateBanner.classList.add("hidden");
  }
});

codeInput.addEventListener("scroll", () => {
  editorGutter.scrollTop = codeInput.scrollTop;
});

// File Tab & Language Change Indicator
langSelect.addEventListener("change", () => {
  const extMap = {
    python: "artefact.py",
    javascript: "snippet.js",
    typescript: "module.ts",
    go: "main.go",
    java: "Service.java",
    json: "payload.json",
    sql: "query.sql",
  };
  fileTabLabel.textContent = extMap[langSelect.value] || "code.txt";
});

// =============================================================================
// Presets & Hero Fast Actions
// =============================================================================
btnPresetDb.addEventListener("click", () => {
  codeInput.value = DEFAULT_SECRET_SNIPPET;
  langSelect.value = "python";
  fileTabLabel.textContent = "artefact.py";
  intentInput.value = "Connect application database securely";
  updateEditorStats();
  emptyStateBanner.classList.add("hidden");
  smoothScrollTo(viewInput);
});

btnPresetSql.addEventListener("click", () => {
  codeInput.value = DEFAULT_SQL_SNIPPET;
  langSelect.value = "python";
  fileTabLabel.textContent = "artefact.py";
  intentInput.value = "User authentication query";
  updateEditorStats();
  emptyStateBanner.classList.add("hidden");
  smoothScrollTo(viewInput);
});

btnPresetClear.addEventListener("click", () => {
  codeInput.value = "";
  intentInput.value = "";
  updateEditorStats();
  codeInput.focus();
});

btnHeroStart.addEventListener("click", () => {
  smoothScrollTo(viewInput);
  codeInput.focus();
});

btnHeroDemo.addEventListener("click", () => {
  btnPresetDb.click();
  btnReview.click();
});

// =============================================================================
// View State Switcher
// =============================================================================
function showView(viewName) {
  viewInput.classList.add("hidden");
  viewLoading.classList.add("hidden");
  viewResult.classList.add("hidden");
  viewError.classList.add("hidden");

  if (viewName === "input") {
    viewInput.classList.remove("hidden");
  } else if (viewName === "loading") {
    viewLoading.classList.remove("hidden");
  } else if (viewName === "result") {
    viewResult.classList.remove("hidden");
    smoothScrollTo(viewResult);
  } else if (viewName === "error") {
    viewError.classList.remove("hidden");
    smoothScrollTo(viewError);
  }
}

// =============================================================================
// Voice Status Probe
// =============================================================================
async function probeVoiceStatus() {
  try {
    const res = await fetch("/api/voice/status");
    if (res.ok) {
      const data = await res.json();
      voiceConfigured = data.voice && data.voice.configured;
      if (btnVoiceExplain) {
        if (voiceConfigured) {
          btnVoiceExplain.title = "Listen to AI Voice Tutor explanation (ElevenLabs Active)";
        } else {
          btnVoiceExplain.title = "Listen to Voice explanation (Browser Speech Mode - ElevenLabs optional)";
        }
      }
    }
  } catch (err) {
    voiceConfigured = false;
  }
}

// =============================================================================
// Dynamic Finding Snippet Highlighting
// =============================================================================
function renderSnippetLine(code, location, title) {
  if (!findingSnippetContent) return;

  const lines = code.split("\n");
  let lineIdx = 0;
  const match = (location || "").match(/line\s*(\d+)/i);
  if (match) {
    lineIdx = Math.max(0, parseInt(match[1], 10) - 1);
  }

  const flaggedCode = lines[lineIdx] !== undefined ? lines[lineIdx] : lines[0] || code;
  const displayLineNum = lineIdx + 1;

  findingSnippetContent.innerHTML = `
    <div class="snippet-line highlighted-danger">
      <span class="line-num">${displayLineNum}</span>
      <span class="line-code"><code>${escapeHtml(flaggedCode)}</code></span>
      <span class="line-flag-badge">⚠️ ${escapeHtml(title || "Potential Risk")}</span>
    </div>
  `;
}

// =============================================================================
// Dynamic Grounding Evidence Display
// =============================================================================
function renderGroundingData(finding, code) {
  const ev = finding.evidence;

  if (ev && ev.grounded) {
    if (findingCwePill) findingCwePill.textContent = ev.cwe || "Official Standard";
    if (pipeFindingVal) pipeFindingVal.textContent = finding.title || "Finding";
    if (pipeRuleVal) pipeRuleVal.textContent = `${ev.cwe || 'CWE'} Standard`;
    if (pipeEvidenceVal) pipeEvidenceVal.textContent = ev.source ? (ev.source.name || "OWASP Top 10") : "Authoritative Standard";
    if (findingSourcePill) findingSourcePill.textContent = "Authoritative Guidance";
    if (findingSourceRef) findingSourceRef.textContent = `${ev.source ? ev.source.name : 'Security Standard'} (${ev.cwe || ev.rule_id || 'Official'})`;
    if (findingEvidenceText) findingEvidenceText.textContent = `"${ev.evidence || 'Authoritative standard guidance applied.'}"`;
    if (findingApplicabilityText) {
      findingApplicabilityText.innerHTML = escapeHtml(ev.why_it_applies || finding.why_it_matters || "Matches official security pattern.");
    }
  } else {
    // Ungrounded or fallback — display cleanly without fabricating evidence
    const categoryName = (finding.category || "General Best Practice").toUpperCase();
    if (findingCwePill) findingCwePill.textContent = categoryName;
    if (pipeFindingVal) pipeFindingVal.textContent = finding.title || "Review Finding";
    if (pipeRuleVal) pipeRuleVal.textContent = "Standard Best Practice";
    if (pipeEvidenceVal) pipeEvidenceVal.textContent = "VeriForge Engine";
    if (findingSourcePill) findingSourcePill.textContent = "Review Engine";
    if (findingSourceRef) findingSourceRef.textContent = "Static & Semantic Code Analysis";
    
    const fallbackText = ev && ev.reason
      ? `Grounding check: ${ev.reason}. VeriForge enforces a strict confidence threshold and avoids hallucinated citations when authoritative standards do not directly match.`
      : (typeof ev === "string" ? ev : "No direct official standard threshold reached for this finding. Follow the actionable recommendations and remediation guidelines above.");
    
    if (findingEvidenceText) findingEvidenceText.textContent = fallbackText;
    if (findingApplicabilityText) {
      findingApplicabilityText.innerHTML = escapeHtml(finding.why_it_matters || "Applies to maintainability, correctness, and defensive coding standards.");
    }
  }
}

// =============================================================================
// Recommended Fix Engine Integration (/api/v1/fix)
// =============================================================================
async function loadFixForFinding(code, finding, language) {
  if (diffBeforeCode) diffBeforeCode.textContent = code;
  if (diffBeforeTag) diffBeforeTag.textContent = `- ${finding.location || 'Original Code'}`;
  if (diffAfterCode) diffAfterCode.textContent = "Generating safe remediation...";
  if (diffAfterTag) diffAfterTag.textContent = "+ Recommended Safe Code";

  // Reset verification badge and result
  if (fixVerifyBadge) fixVerifyBadge.style.display = "none";
  if (fixVerifyResultBox) {
    fixVerifyResultBox.className = "quiz-feedback hidden";
    fixVerifyResultBox.textContent = "";
  }

  try {
    const res = await fetch("/api/v1/fix", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: code,
        finding_id: finding.id,
        finding_title: finding.title,
        language: language || "python"
      })
    });

    if (res.ok) {
      const data = await res.json();
      currentFixedCode = data.fixed_code || code;
      if (diffAfterCode) diffAfterCode.textContent = currentFixedCode;
      if (findingFixGuidance) {
        findingFixGuidance.textContent = data.explanation || finding.recommendation || "Applied safe code remediation.";
      }
      if (btnCopyFixCode) btnCopyFixCode.style.display = "inline-flex";
    } else {
      // Deterministic fix not available (e.g. clean code or complex architectural refactor)
      currentFixedCode = finding.recommendation ? `# Recommendation:\n# ${finding.recommendation}\n\n${code}` : code;
      if (diffAfterCode) diffAfterCode.textContent = currentFixedCode;
      if (findingFixGuidance) {
        findingFixGuidance.textContent = finding.recommendation || "Inspect and follow recommended engineering practices.";
      }
    }
  } catch (err) {
    currentFixedCode = code;
    if (diffAfterCode) diffAfterCode.textContent = finding.recommendation || code;
    if (findingFixGuidance) {
      findingFixGuidance.textContent = finding.recommendation || "Inspect code according to the finding guidelines.";
    }
  }
}

// =============================================================================
// Automated Fix Verification Engine (/api/v1/verify)
// =============================================================================
async function runVerifyFixWithEngine() {
  if (!btnRunVerifyFix || !fixVerifyResultBox) return;

  if (!currentFixedCode || currentFixedCode.trim() === currentOriginalCode.trim()) {
    fixVerifyResultBox.className = "quiz-feedback warning";
    fixVerifyResultBox.textContent = "No remediation changes to verify against the original code.";
    fixVerifyResultBox.classList.remove("hidden");
    return;
  }

  fixVerifyResultBox.className = "quiz-feedback warning";
  fixVerifyResultBox.textContent = "Testing modified code against the VeriForge review engine...";
  fixVerifyResultBox.classList.remove("hidden");

  try {
    const res = await fetch("/api/v1/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_code: currentOriginalCode,
        fixed_code: currentFixedCode,
        original_finding_title: currentFinding ? currentFinding.title : "",
        language: langSelect.value || "python"
      })
    });

    if (res.ok) {
      const data = await res.json();
      if (data.is_resolved) {
        fixVerifyResultBox.className = "quiz-feedback success";
        fixVerifyResultBox.textContent = `✓ ${data.message || 'Issue resolved: The original finding is no longer detected.'}`;
        if (fixVerifyBadge) {
          fixVerifyBadge.className = "verify-status-chip verified";
          fixVerifyBadge.textContent = "✓ Fix Verified by Engine";
          fixVerifyBadge.style.display = "inline-flex";
        }
      } else {
        fixVerifyResultBox.className = "quiz-feedback warning";
        fixVerifyResultBox.textContent = `⚠️ ${data.message || 'Issue still detected in modified code.'}`;
        if (fixVerifyBadge) {
          fixVerifyBadge.className = "verify-status-chip";
          fixVerifyBadge.textContent = "Check Required";
          fixVerifyBadge.style.display = "inline-flex";
        }
      }
    } else {
      const errData = await res.json().catch(() => ({}));
      fixVerifyResultBox.className = "quiz-feedback warning";
      fixVerifyResultBox.textContent = `Verification notice: ${errData.detail || 'Unable to complete automated check.'}`;
    }
  } catch (err) {
    fixVerifyResultBox.className = "quiz-feedback warning";
    fixVerifyResultBox.textContent = "Engine verification network check timed out. Please try again.";
  }
}

if (btnRunVerifyFix) {
  btnRunVerifyFix.addEventListener("click", runVerifyFixWithEngine);
}

// =============================================================================
// Dynamic Comprehension Quiz Generator
// =============================================================================
function renderComprehensionQuiz(finding) {
  if (!quizQuestionText || !quizChoicesContainer) return;

  quizQuestionText.textContent = finding.verification_question || "Why is addressing this issue important?";

  const cat = (finding.category || "").toLowerCase();
  const title = (finding.title || "").toLowerCase();

  let options = [];
  let correctKey = "B";

  if (cat.includes("secret") || title.includes("credential") || title.includes("password")) {
    correctKey = "B";
    options = [
      { key: "A", text: "Hardcoded credentials make the program run slower in production.", explanation: "Not quite. Hardcoded credentials have no measurable impact on execution speed. The actual danger is credential exposure in source control." },
      { key: "B", text: "Anyone with access to the source code or build history can extract the plaintext secret.", explanation: "✓ Correct — committing secrets to source control exposes them to all collaborators, build systems, and repository history." },
      { key: "C", text: "Python variables are technically unable to store password strings.", explanation: "Not quite. Python variables easily store strings; the problem is publishing sensitive credentials in repository files." },
      { key: "D", text: "It causes memory fragmentation in the application heap.", explanation: "Not quite. A short string credential does not cause memory fragmentation. The risk is security exposure." }
    ];
  } else if (cat.includes("sql") || title.includes("sql")) {
    correctKey = "B";
    options = [
      { key: "A", text: "Concatenating strings in queries slows down network connection speed.", explanation: "Not quite. Network speed is unrelated. The risk is allowing user input to modify SQL syntax." },
      { key: "B", text: "Untrusted user input can alter SQL syntax, enabling unauthorized data access or deletion.", explanation: "✓ Correct — parameterized queries separate SQL code logic from data literals, preventing attackers from modifying query structure." },
      { key: "C", text: "Database drivers automatically reject queries containing string concatenation.", explanation: "Not quite. Most drivers will execute the concatenated string directly, which is precisely why SQL injection happens." },
      { key: "D", text: "String concatenation causes database table locks to fail.", explanation: "Not quite. String concatenation does not affect table locks; it allows query hijacking." }
    ];
  } else if (cat.includes("command") || title.includes("eval") || title.includes("exec")) {
    correctKey = "A";
    options = [
      { key: "A", text: "It executes arbitrary user-controlled code or system commands directly inside the runtime.", explanation: "✓ Correct — eval() and exec() parse strings as executable code, giving attackers full control over the runtime process." },
      { key: "B", text: "Dynamic code execution reduces hard drive storage space rapidly.", explanation: "Not quite. Disk space is unaffected. The critical risk is arbitrary remote code execution." },
      { key: "C", text: "Modern operating systems strictly prohibit executing dynamic code.", explanation: "Not quite. Operating systems will execute what the Python runtime requests, allowing attackers to execute commands." },
      { key: "D", text: "It changes the network port of the host web server.", explanation: "Not quite. eval() executes arbitrary Python logic, not port bindings." }
    ];
  } else if (cat.includes("maintainability") || title.includes("except")) {
    correctKey = "A";
    options = [
      { key: "A", text: "Bare except: blocks catch all exceptions blindly, masking typos, interrupts, and critical bugs.", explanation: "✓ Correct — catching generic exceptions conceals unexpected failures and makes debugging difficult." },
      { key: "B", text: "Python raises a syntax error when an unadorned except: clause is parsed.", explanation: "Not quite. Bare except: is valid Python syntax, but considered bad practice because it swallows errors." },
      { key: "C", text: "It prevents memory garbage collection from reclaiming freed objects.", explanation: "Not quite. Memory management is unaffected; error visibility is compromised." },
      { key: "D", text: "It causes the interpreter to re-compile the script repeatedly.", explanation: "Not quite. The interpreter compiles normally; debugging is severely hindered." }
    ];
  } else {
    correctKey = "B";
    options = [
      { key: "A", text: "Following this guidance replaces the need for automated tests.", explanation: "Not quite. Code quality best practices complement tests but do not replace them." },
      { key: "B", text: "Adhering to standard patterns reduces defects, aids maintainability, and prevents regressions.", explanation: "✓ Correct — structured patterns and clear design make code reliable and resilient over time." },
      { key: "C", text: "It automatically resolves compiler warnings in unrelated modules.", explanation: "Not quite. Guidance addresses only the specific inspected logic." },
      { key: "D", text: "It increases network bandwidth between client and server.", explanation: "Not quite. Network bandwidth is determined by infrastructure, not internal code structure." }
    ];
  }

  // Render buttons
  let choicesHtml = "";
  options.forEach((opt) => {
    choicesHtml += `
      <button type="button" class="quiz-choice" data-choice="${opt.key}" role="radio" aria-checked="false">
        <span class="choice-key">${opt.key}</span>
        <span class="choice-val">${escapeHtml(opt.text)}</span>
      </button>
    `;
  });
  quizChoicesContainer.innerHTML = choicesHtml;

  // Rebind listeners
  const renderedButtons = quizChoicesContainer.querySelectorAll(".quiz-choice");
  renderedButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const chosenKey = btn.getAttribute("data-choice");
      const chosenOpt = options.find((o) => o.key === chosenKey);

      renderedButtons.forEach((b) => {
        b.setAttribute("aria-checked", "false");
        b.classList.remove("selected-correct", "selected-incorrect");
      });

      btn.setAttribute("aria-checked", "true");

      if (chosenKey === correctKey) {
        btn.classList.add("selected-correct");
        quizFeedbackBox.className = "quiz-feedback success";
        quizFeedbackBox.textContent = chosenOpt.explanation;

        verifyChipStatus.className = "verify-status-chip verified";
        verifyChipStatus.textContent = "✓ Verified by Builder";
      } else {
        btn.classList.add("selected-incorrect");
        quizFeedbackBox.className = "quiz-feedback warning";
        quizFeedbackBox.textContent = chosenOpt.explanation;

        verifyChipStatus.className = "verify-status-chip";
        verifyChipStatus.textContent = "Check Required";
      }
    });
  });
}

// =============================================================================
// Review Pipeline Orchestration
// =============================================================================
function setStepState(stepEl, status, icon) {
  stepEl.classList.remove("active", "done", "pending");
  stepEl.classList.add(status);
  const ind = stepEl.querySelector(".step-indicator");
  if (ind) ind.textContent = icon;
}

async function runReviewPipeline(code) {
  showView("loading");
  currentOriginalCode = code;

  setStepState(step1, "active", "●");
  setStepState(step2, "pending", "○");
  setStepState(step3, "pending", "○");
  setStepState(step4, "pending", "○");
  loadingStageLabel.textContent = "Analyzing your code...";

  try {
    const payload = {
      artefact: code,
      language: langSelect.value,
      context: intentInput.value || ""
    };

    setStepState(step1, "done", "✓");
    setStepState(step2, "active", "●");
    loadingStageLabel.textContent = "Checking security patterns...";

    const res = await fetch("/api/v1/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Review API failed with status ${res.status}`);
    }

    setStepState(step2, "done", "✓");
    setStepState(step3, "active", "●");
    loadingStageLabel.textContent = "Finding potential vulnerabilities...";

    const data = await res.json();

    setStepState(step3, "done", "✓");
    setStepState(step4, "active", "●");
    loadingStageLabel.textContent = "Grounding findings with trusted sources...";

    setTimeout(async () => {
      setStepState(step4, "done", "✓");
      
      const findings = data.findings || [];
      metricTotalIssues.textContent = findings.length < 10 ? '0' + findings.length : findings.length;

      let c = 0, h = 0, m = 0, l = 0;
      let primaryFinding = null;

      findings.forEach(f => {
        const sev = (f.severity || '').toLowerCase();
        if (sev === 'critical') c++;
        else if (sev === 'high') h++;
        else if (sev === 'medium') m++;
        else l++;

        if (!primaryFinding) {
          primaryFinding = f;
        } else {
          const rank = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0};
          const pRank = rank[(primaryFinding.severity || '').toLowerCase()] || 0;
          const currRank = rank[sev] || 0;
          if (currRank > pRank) primaryFinding = f;
        }
      });

      metricCritical.textContent = c < 10 ? '0' + c : c;
      const metricHighEl = document.getElementById("metric-high");
      const metricMedEl = document.getElementById("metric-medium");
      const metricLowEl = document.getElementById("metric-low");
      if (metricHighEl) metricHighEl.textContent = h < 10 ? '0' + h : h;
      if (metricMedEl) metricMedEl.textContent = m < 10 ? '0' + m : m;
      if (metricLowEl) metricLowEl.textContent = l < 10 ? '0' + l : l;

      currentFinding = primaryFinding;

      if (primaryFinding) {
        findingSeverityPill.innerHTML = `<span class="pulse-dot"></span><span>${(primaryFinding.severity || 'INFO').toUpperCase()}</span>`;
        findingSeverityPill.className = `severity-pill ${(primaryFinding.severity || 'info').toLowerCase()}`;
        
        const locPill = document.getElementById("finding-loc-pill");
        if (locPill) locPill.textContent = primaryFinding.location || 'Unknown Location';

        findingTitle.textContent = primaryFinding.title || 'Review Finding';
        findingPlainExplanation.textContent = primaryFinding.description || 'No description provided.';
        findingWhyMatters.textContent = primaryFinding.why_it_matters || 'No explanation provided.';

        // 1. Highlight flagged snippet line
        renderSnippetLine(code, primaryFinding.location, primaryFinding.title);

        // 2. Render Grounding
        renderGroundingData(primaryFinding, code);

        // 3. Load Recommended Fix from API
        await loadFixForFinding(code, primaryFinding, langSelect.value);

        // 4. Render Dynamic Comprehension Quiz
        renderComprehensionQuiz(primaryFinding);
      }

      showView("result");
      resetResultUI();
    }, 450);

  } catch (err) {
    console.error(err);
    errorMessage.textContent = err.message || "The review service was unable to complete the analysis. Please check your connection or try again.";
    showView("error");
  }
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
      if (panel) panel.classList.remove("expanded");
    } else {
      trigger.setAttribute("aria-expanded", "true");
      if (panel) panel.classList.add("expanded");
    }
  });
});

// =============================================================================
// Copy Recommended Fix
// =============================================================================
btnCopyFixCode.addEventListener("click", async () => {
  const textToCopy = currentFixedCode || (diffAfterCode ? diffAfterCode.textContent : "");
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(textToCopy);
    } else {
      const ta = document.createElement("textarea");
      ta.value = textToCopy;
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

function resetResultUI() {
  accordionTriggers.forEach((t) => {
    t.setAttribute("aria-expanded", "true");
    const p = document.getElementById(t.getAttribute("aria-controls"));
    if (p) p.classList.add("expanded");
  });

  copyBtnText.textContent = "Copy Fix";
  quizFeedbackBox.className = "quiz-feedback hidden";
  quizFeedbackBox.textContent = "";

  verifyChipStatus.className = "verify-status-chip";
  verifyChipStatus.textContent = "Pending Check";

  voiceAlertBanner.classList.add("hidden");
  stopVoiceAudio();
}

// =============================================================================
// Voice Explanation (ElevenLabs Integration with Resilient Fallback)
// =============================================================================
let isVoicePlaying = false;

function stopVoiceAudio() {
  isVoicePlaying = false;
  if (btnVoiceExplain) {
    btnVoiceExplain.classList.remove("speaking");
  }
  if (voiceLabel) {
    voiceLabel.textContent = "🔊 Explain this to me";
  }

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

  const explanationText = findingPlainExplanation ? findingPlainExplanation.textContent.trim() : "";
  if (!explanationText) return;

  voiceAlertBanner.classList.remove("hidden");
  voiceAlertIcon.textContent = "⏳";
  voiceAlertMsg.textContent = "Connecting to voice service...";

  isVoicePlaying = true;
  if (btnVoiceExplain) btnVoiceExplain.classList.add("speaking");
  if (voiceLabel) voiceLabel.textContent = "Generating audio...";

  // 1. Attempt backend ElevenLabs endpoint
  let backendSuccess = false;
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2800);

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
      if (voiceLabel) voiceLabel.textContent = "Stop voice audio";
      backendSuccess = true;

      backendAudioPlayer.onended = () => {
        stopVoiceAudio();
        voiceAlertBanner.classList.add("hidden");
      };
    }
  } catch (err) {
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
        if (voiceLabel) voiceLabel.textContent = "Stop voice audio";
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
      voiceAlertMsg.textContent = "Voice audio is currently unavailable.";
      stopVoiceAudio();
    }
  }
}

if (btnVoiceExplain) {
  btnVoiceExplain.addEventListener("click", handleVoiceExplanation);
}

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
  probeVoiceStatus();
});
