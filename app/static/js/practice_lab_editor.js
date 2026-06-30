// Monaco Editor integration for the Practice Lab frontend.
// Replaces CodeMirror 6 implementation.

(function () {
  const MONACO_CDN_LOADER_URL =
    "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.0/min/vs/loader.js";

  const FALLBACK_TEXTAREA_LINE_HEIGHT = 24;

  function getStarterOrFallback({ starterCode }) {
    if (starterCode && String(starterCode).trim().length > 0) return String(starterCode);
    return "# Write your solution here\n";
  }

  function storageKey(questionId) {
    return `practice_lab_${questionId}`;
  }

  function readFromLocalStorage(questionId, starterCode) {
    const key = storageKey(questionId);
    try {
      const saved = window.localStorage.getItem(key);
      if (saved !== null && saved !== undefined) return saved;
    } catch (_) {
      // ignore
    }
    return getStarterOrFallback({ starterCode });
  }

  function persistToLocalStorage(questionId, value) {
    const key = storageKey(questionId);
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {
      // ignore
    }
  }

  function refreshIcons() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  // Ensure we don't load/initialize Monaco multiple times.
  let monacoLoadPromise = null;
  function loadMonacoOnce() {
    if (monacoLoadPromise) return monacoLoadPromise;

    monacoLoadPromise = new Promise((resolve, reject) => {
      // If monaco is already present, resolve immediately.
      if (window.monaco && window.monaco.editor && window.monaco.languages) {
        resolve(window.monaco);
        return;
      }

      // Load AMD loader if needed.
      const existingLoader = document.querySelector(
        'script[data-monaco-loader="true"]'
      );

      const loadLoader = () => {
        return new Promise((loaderResolve, loaderReject) => {
          const script = document.createElement("script");
          script.src = MONACO_CDN_LOADER_URL;
          script.async = true;
          script.type = "text/javascript";
          script.setAttribute("data-monaco-loader", "true");

          script.onload = () => loaderResolve();
          script.onerror = () => loaderReject(new Error("Failed to load Monaco loader"));

          document.head.appendChild(script);
        });
      };

      const afterLoaderReady = () => {
        try {
          // Monaco AMD expects require + config.
          if (!window.require) {
            reject(new Error("Monaco AMD loader is not available (window.require missing)"));
            return;
          }

          // Configure baseUrl only if not already configured.
          // (Avoid overriding if already set by another instance.)
          if (!window.__monacoAmdConfigured) {
            try {
              window.require.config({
                paths: {
                  vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.0/min/vs",
                },
              });
              window.__monacoAmdConfigured = true;
            } catch (_) {
              // ignore; proceed
            }
          }

          window.require(["vs/editor/editor.main"], () => {
            if (window.monaco && window.monaco.editor) resolve(window.monaco);
            else reject(new Error("Monaco loaded but not fully available"));
          });
        } catch (e) {
          reject(e);
        }
      };

      if (existingLoader) {
        // Loader script already added; wait a tick and attempt require.
        window.setTimeout(afterLoaderReady, 50);
        return;
      }

      loadLoader()
        .then(afterLoaderReady)
        .catch(reject);
    });

    return monacoLoadPromise;
  }

  function createTextareaFallback({ editorHost, initialValue }) {
    editorHost.innerHTML = "";

    const textarea = document.createElement("textarea");
    textarea.className = "form-control";
    textarea.value = initialValue;
    textarea.spellcheck = false;
    textarea.style.minHeight = `${Math.max(10, Math.floor(450 / FALLBACK_TEXTAREA_LINE_HEIGHT)) * FALLBACK_TEXTAREA_LINE_HEIGHT}px`;
    textarea.style.resize = "vertical";

    editorHost.appendChild(textarea);

    return {
      kind: "fallback",
      getValue: () => textarea.value,
      setValue: (value) => {
        textarea.value = value;
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
      },
      layout: () => {},
      onDidChangeContent: (handler) => {
        textarea.addEventListener("input", () => handler());
      },
    };
  }

  async function mountMonacoEditor({ editorHost, questionId, starterCode }) {
    // Restore/initialize code.
    const initialValue = readFromLocalStorage(questionId, starterCode);

    // Monaco host must have a size; ensure some height.
    // This avoids editors with height=0 depending on template CSS.
    editorHost.style.height = editorHost.style.height || "450px";

    const monaco = await loadMonacoOnce();

    // Create editor.
    const editor = monaco.editor.create(editorHost, {
      value: initialValue,
      language: "python",
      theme: "vs-dark",
      automaticLayout: true,
      minimap: { enabled: false },
      lineNumbers: "on",
      scrollBeyondLastLine: false,
      // Let users type.
      readOnly: false,
    });

    // Autosave: debounce ~200ms like the old implementation.
    let saveTimer = null;
    editor.onDidChangeModelContent(() => {
      if (saveTimer) window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => {
        persistToLocalStorage(questionId, editor.getValue());
      }, 200);
    });

    return {
      kind: "monaco",
      getValue: () => editor.getValue(),
      setValue: (value) => {
        editor.setValue(value);
        persistToLocalStorage(questionId, value);
      },
      layout: () => editor.layout(),
      focus: () => editor.focus(),
      onReady: () => {},
    };
  }

  function outputKind({ ok, data, timedOut = false }) {
    const stderr = String(data && data.stderr ? data.stderr : "");
    if (timedOut || /timeout|timed out/i.test(stderr)) return "timeout";
    if (ok && data && data.success) return "success";
    if (/SyntaxError|IndentationError|TabError/i.test(stderr)) return "syntax";
    return "runtime";
  }

  function outputLabel(kind) {
    if (kind === "idle") return "Ready";
    if (kind === "success") return "Success";
    if (kind === "syntax") return "Syntax Error";
    if (kind === "timeout") return "Timeout";
    if (kind === "running") return "Running...";
    return "Runtime Error";
  }

  function setOutputStatus(statusEl, kind) {
    if (!statusEl) return;
    statusEl.textContent = outputLabel(kind);
    statusEl.className = `practice-lab-output-status status-${kind}`;
  }

  function setRunningState(runBtn, isRunning) {
    if (!runBtn) return;
    const label = runBtn.querySelector(".practice-lab-run-label");
    runBtn.disabled = isRunning;
    runBtn.classList.toggle("is-running", isRunning);
    if (label) label.textContent = isRunning ? "Running..." : "Submit Code";
  }

  function wireHints({ root }) {
    const hintBtn = document.getElementById("practice_lab_hint_btn");
    const modal = document.getElementById("practice_lab_hints_modal");
    const panel = modal ? modal.querySelector(".practice-lab-modal-panel") : null;
    const body = document.getElementById("practice_lab_hints_body");
    const closeEls = modal ? modal.querySelectorAll("[data-practice-lab-close-hints]") : [];
    if (!hintBtn || !modal || !panel || !body) return;

    let hints = [];
    try {
      const rawMetadata = JSON.parse(root.dataset.hintsMetadata || "\"\"");
      const metadata = rawMetadata ? JSON.parse(rawMetadata) : {};
      hints = Array.isArray(metadata.hints) ? metadata.hints : [];
    } catch (_) {
      hints = [];
    }

    function renderHints() {
      body.innerHTML = "";
      if (!Array.isArray(hints) || hints.length === 0) {
        const empty = document.createElement("p");
        empty.textContent = "Hints are not available for this question yet.";
        body.appendChild(empty);
        return;
      }

      const list = document.createElement("ol");
      hints.forEach((hint) => {
        const item = document.createElement("li");
        item.textContent = String(hint);
        list.appendChild(item);
      });
      body.appendChild(list);
    }

    function openHints() {
      renderHints();
      modal.hidden = false;
      document.body.classList.add("practice-lab-modal-open");
      window.setTimeout(() => panel.focus(), 0);
    }

    function closeHints() {
      modal.hidden = true;
      document.body.classList.remove("practice-lab-modal-open");
      hintBtn.focus();
    }

    hintBtn.addEventListener("click", openHints);
    closeEls.forEach((el) => el.addEventListener("click", closeHints));
    document.addEventListener("keydown", (event) => {
      if (!modal.hidden && event.key === "Escape") closeHints();
    });
  }

  function wireFullscreen({ editorRef }) {
    const fullscreenBtn = document.getElementById("practice_lab_fullscreen_btn");
    const editorCard = document.querySelector(".practice-lab-editor-card");
    if (!fullscreenBtn || !editorCard) return;

    function updateFullscreenButton() {
      const isFullscreen = document.fullscreenElement === editorCard;
      fullscreenBtn.setAttribute(
        "aria-label",
        isFullscreen ? "Exit fullscreen editor" : "Enter fullscreen editor"
      );
      fullscreenBtn.setAttribute(
        "title",
        isFullscreen ? "Exit fullscreen editor" : "Fullscreen editor"
      );
      fullscreenBtn.innerHTML = isFullscreen
        ? '<i data-lucide="minimize-2"></i>'
        : '<i data-lucide="maximize-2"></i>';
      refreshIcons();
      window.setTimeout(() => {
        if (editorRef.layout) editorRef.layout();
        if (isFullscreen && editorRef.focus) editorRef.focus();
      }, 80);
    }

    fullscreenBtn.addEventListener("click", async () => {
      try {
        if (document.fullscreenElement === editorCard) {
          await document.exitFullscreen();
        } else {
          await editorCard.requestFullscreen();
        }
      } catch (_) {
        // Browser may block fullscreen in unsupported contexts.
      }
    });

    document.addEventListener("fullscreenchange", updateFullscreenButton);
    updateFullscreenButton();
  }

  function wireRunButton({ root, editorRef, outputPanel }) {
    const runBtn = document.getElementById("practice_lab_run_btn");
    const resetBtn = document.getElementById("practice_lab_reset_btn");

    const execTimeEl = document.getElementById("practice_lab_execution_time");
    const exitCodeEl = document.getElementById("practice_lab_exit_code");
    const errorsEl = document.getElementById("practice_lab_errors");
    const statusEl = document.getElementById("practice_lab_output_status");

    function safeSetText(el, value) {
      if (!el) return;
      el.textContent = value === undefined || value === null ? "-" : String(value);
    }

    function formatExecutionTime(value) {
      const numeric = Number(value);
      if (!Number.isFinite(numeric)) return "-";
      return `${numeric.toFixed(3)}s`;
    }

    if (!runBtn || !outputPanel) return;

    // Ensure correct visual state: enable the button only when editor is ready.
    runBtn.removeAttribute("disabled");
    runBtn.classList.remove("button-secondary");
    runBtn.classList.add("button-primary");

    safeSetText(execTimeEl, "-");
    safeSetText(exitCodeEl, "-");
    if (errorsEl) errorsEl.textContent = "";
    outputPanel.textContent = "Run your code to see output.";
    setOutputStatus(statusEl, "idle");

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        if (!window.confirm("Reset your code to the starter template?")) return;
        const questionId = root.dataset.questionId;
        const starterCode = getStarterOrFallback({ starterCode: root.dataset.starterCode || "" });
        editorRef.setValue(starterCode);
        try {
          window.localStorage.setItem(`practice_lab_${questionId}`, starterCode);
        } catch (_) {
          // ignore
        }
        if (editorRef.focus) editorRef.focus();
      });
    }

    async function runCurrentCode() {
      if (runBtn.disabled) return;
      setRunningState(runBtn, true);
      outputPanel.textContent = "Running...";
      safeSetText(execTimeEl, "-");
      safeSetText(exitCodeEl, "-");
      if (errorsEl) errorsEl.textContent = "";
      setOutputStatus(statusEl, "running");

      try {
        const questionId = root.dataset.questionId;
        const code = editorRef.getValue(); // Requirement

        const resp = await fetch("/api/practice-lab/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
          body: JSON.stringify({
            question_id: Number(questionId),
            code,
            stdin: "",
            timeout: 5,
          }),
        });

        const data = await resp.json().catch(() => ({}));

        if (!resp.ok || !data.success) {
          const stderr = data.stderr ? String(data.stderr) : "";
          const msg = stderr || data.stderr || data.stdout || `Request failed (${resp.status})`;
          setOutputStatus(statusEl, outputKind({ ok: false, data }));
          outputPanel.textContent = msg;
          safeSetText(exitCodeEl, data.exit_code);
          safeSetText(execTimeEl, formatExecutionTime(data.execution_time));
          if (errorsEl) errorsEl.textContent = stderr;
          return;
        }

        const stdout = data.stdout ? String(data.stdout) : "";
        const stderr = data.stderr ? String(data.stderr) : "";
        const exitCode = data.exit_code;

        let out = "";
        if (stdout) out += stdout;
        if (stderr) {
          if (out) out += "\n";
          out += stderr;
        }
        if (!out) out = "(no output)";
        setOutputStatus(statusEl, outputKind({ ok: true, data }));
        outputPanel.textContent = out;
        safeSetText(exitCodeEl, exitCode);
        safeSetText(execTimeEl, formatExecutionTime(data.execution_time));
        if (errorsEl) errorsEl.textContent = stderr;
      } catch (err) {
        setOutputStatus(statusEl, "runtime");
        outputPanel.textContent = `Execution error: ${err}`;
        if (errorsEl) errorsEl.textContent = String(err);
      } finally {
        setRunningState(runBtn, false);
      }
    }

    runBtn.addEventListener("click", runCurrentCode);
    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        runCurrentCode();
      }
    });
  }

  async function setupEditor() {
    const root = document.getElementById("practice_lab_editor_root");
    if (!root) {
      console.warn("[practice_lab_editor] root not found");
      return;
    }

    const questionId = root.dataset.questionId;
    const starterCode = root.dataset.starterCode || "";

    const editorHost = document.getElementById("practice_lab_editor");
    if (!editorHost) {
      console.warn("[practice_lab_editor] editor host not found");
      return;
    }

    const outputPanel = document.getElementById("practice_lab_output");

    // Keep button disabled until Monaco is ready; fallback will enable too.
    const runBtn = document.getElementById("practice_lab_run_btn");
    if (runBtn) runBtn.setAttribute("disabled", "disabled");

    let editorRef = null;

    try {
      editorRef = await mountMonacoEditor({
        editorHost,
        questionId,
        starterCode,
      });

      if (outputPanel) {
        wireRunButton({ root, editorRef, outputPanel });
      }
      wireHints({ root });
      wireFullscreen({ editorRef });
    } catch (e) {
      console.error("[practice_lab_editor] Monaco failed; falling back to textarea", e);

      const initialValue = readFromLocalStorage(questionId, starterCode);
      editorRef = createTextareaFallback({ editorHost, initialValue });

      if (outputPanel) {
        wireRunButton({ root, editorRef, outputPanel });
      }
      wireHints({ root });
      wireFullscreen({ editorRef });
    }
  }

  document.addEventListener("DOMContentLoaded", setupEditor);
})();

