import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime

def create_log(log : str):
    return f'<p class="run">{log}</p>'

terminal_html = """
<style>
/* Hidden checkbox acts as the toggle state */
#toggleTerminal {
    display: none;
}

/* Terminal container */
.terminal-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 220px;
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: "Consolas", monospace;
    border-top: 1px solid #333;
    display: flex;
    flex-direction: column;
    transition: height 0.3s ease;
    z-index: 9999;
    overflow: hidden;
}

/* When checkbox is NOT checked → expanded */
#toggleTerminal:not(:checked) ~ .terminal-container {
    height: 220px;
}

/* When checkbox IS checked → minimized */
#toggleTerminal:checked ~ .terminal-container {
    height: 32px;
}

/* Terminal header */
.terminal-header {
    background: #2d2d2d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.3rem 0.8rem;
    color: #ccc;
    font-size: 0.9rem;
    user-select: none;
}

/* The clickable toggle button */
.terminal-toggle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    background: #27c93f;
    cursor: pointer;
    transition: background 0.2s ease;
}

/* Change color when minimized */
#toggleTerminal:checked ~ .terminal-container .terminal-toggle {
    background: #ffbd2e;
}

.terminal-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.8rem;
    font-size: 0.9rem;
    line-height: 1.4;
}

.terminal-body p { margin: 0; white-space: pre-wrap; }
.terminal-body p.info { color: #9cdcfe; }
.terminal-body p.action { color: #ce9178; }
.terminal-body p.run { color: #b5cea8; }
</style>

<!-- Hidden toggle input -->
<input type="checkbox" id="toggleTerminal">

<!-- Terminal container -->
<div class="terminal-container" id="terminalContainer">
  <div class="terminal-header">
    <!-- Label controls the checkbox -->
    <label for="toggleTerminal" class="terminal-toggle"></label>
    <span>Logs</span>
    <div></div>
  </div>
  <div class="terminal-body" id="terminalBody">
    {"".join(st.session_state.logs)}
  </div>
</div>
"""
import streamlit as st
import time
from datetime import datetime

# --- Setup state ---
if "logs" not in st.session_state:
    st.session_state.logs = [f'<p class="run">Init {i}</p>' for i in range(5)]

# --- Terminal style (kept constant) ---
terminal_style = """
<style>
/* Hidden checkbox acts as the toggle state */
#toggleTerminal {
    display: none;
}

/* Terminal container */
.terminal-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 220px;
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: "Consolas", monospace;
    border-top: 1px solid #333;
    display: flex;
    flex-direction: column;
    transition: height 0.3s ease;
    z-index: 9999;
    overflow: hidden;
}

/* When checkbox is NOT checked → expanded */
#toggleTerminal:not(:checked) ~ .terminal-container {
    height: 220px;
}

/* When checkbox IS checked → minimized */
#toggleTerminal:checked ~ .terminal-container {
    height: 32px;
}

/* Terminal header */
.terminal-header {
    background: #2d2d2d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.3rem 0.8rem;
    color: #ccc;
    font-size: 0.9rem;
    user-select: none;
}

/* The clickable toggle button */
.terminal-toggle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    background: #27c93f;
    cursor: pointer;
    transition: background 0.2s ease;
}

/* Change color when minimized */
#toggleTerminal:checked ~ .terminal-container .terminal-toggle {
    background: #ffbd2e;
}

.terminal-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.8rem;
    font-size: 0.9rem;
    line-height: 1.4;
}

.terminal-body p { margin: 0; white-space: pre-wrap; }
.terminal-body p.info { color: #9cdcfe; }
.terminal-body p.action { color: #ce9178; }
.terminal-body p.run { color: #b5cea8; }
</style>
"""

# --- Placeholder for rerendering ---
terminal_placeholder = st.empty()

# --- Initial render ---
logs_html = "".join(st.session_state.logs)

terminal_placeholder.html(
    f"""
    {terminal_style}
    <!-- Hidden toggle input -->
    <input type="checkbox" id="toggleTerminal">

    <!-- Terminal container -->
     <!-- nonce: {time.time()} -->
    <div class="terminal-container" id="terminalContainer">
      <div class="terminal-header">
        <!-- Label controls the checkbox -->
        <label for="toggleTerminal" class="terminal-toggle"></label>
        <span>Logs</span>
        <div></div>
      </div>
      <div class="terminal-body" id="terminalBody">
        {logs_html}
      </div>
    </div>
    """)

# --- Simulate appending logs dynamically ---
if st.button("Run process"):
    for i in range(5):
        st.session_state.logs.append(create_log(f"Step {i+1} complete — {datetime.now().strftime("%H:%M:%S")}"))
        logs_html = "".join(st.session_state.logs)

        # rebuild entire HTML each time (nonce changes to force rerender)
        terminal_placeholder.html(
            f"""
    {terminal_style}
    <!-- Hidden toggle input -->
    <input type="checkbox" id="toggleTerminal">

    <!-- Terminal container -->
     <!-- nonce: {time.time()} -->
    <div class="terminal-container" id="terminalContainer">
      <div class="terminal-header">
        <!-- Label controls the checkbox -->
        <label for="toggleTerminal" class="terminal-toggle"></label>
        <span>Logs</span>
        <div></div>
      </div>
      <div class="terminal-body" id="terminalBody">
        {logs_html}
      </div>
    </div>
    """
        )

        time.sleep(0.5)
