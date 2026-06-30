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
      onReady: () => {},
    };
  }

  function wireRunButton({ root, editorRef, outputPanel }) {
    const runBtn = document.getElementById("practice_lab_run_btn");
    const resetBtn = document.getElementById("practice_lab_reset_btn");

    const execTimeEl = document.getElementById("practice_lab_execution_time");
    const exitCodeEl = document.getElementById("practice_lab_exit_code");
    const errorsEl = document.getElementById("practice_lab_errors");

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

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        const questionId = root.dataset.questionId;
        try {
          window.localStorage.removeItem(`practice_lab_${questionId}`);
        } catch (_) {
          // ignore
        }
        window.location.reload();
      });
    }

    runBtn.addEventListener("click", async () => {
      outputPanel.textContent = "Running...";
      safeSetText(execTimeEl, "-");
      safeSetText(exitCodeEl, "-");
      if (errorsEl) errorsEl.textContent = "";


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
        outputPanel.textContent = out;
        safeSetText(exitCodeEl, exitCode);
        safeSetText(execTimeEl, formatExecutionTime(data.execution_time));
        if (errorsEl) errorsEl.textContent = stderr;
      } catch (err) {
        outputPanel.textContent = `Execution error: ${err}`;
        if (errorsEl) errorsEl.textContent = String(err);
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
    } catch (e) {
      console.error("[practice_lab_editor] Monaco failed; falling back to textarea", e);

      const initialValue = readFromLocalStorage(questionId, starterCode);
      editorRef = createTextareaFallback({ editorHost, initialValue });

      if (outputPanel) {
        wireRunButton({ root, editorRef, outputPanel });
      }
    }
  }

  document.addEventListener("DOMContentLoaded", setupEditor);
})();

