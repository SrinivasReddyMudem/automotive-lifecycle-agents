"""Optional real-browser checks: pip install playwright and install Chromium/Edge."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import pytest


def test_copy_matches_rendered_response_including_closed_sections(tmp_path):
    playwright = pytest.importorskip("playwright.sync_api")
    root = Path(__file__).resolve().parents[2]
    app = tmp_path / "copy_demo.py"
    app.write_text('''import sys
sys.path.insert(0, ROOT)
import streamlit as st
from sdk_agents.core.renderer import render_can_bus_analyst
from sdk_agents.core.response_copy import render_copy_button
from sdk_agents.tests.integrator.test_can_bus_analyst import make_valid_output
for i in range(2):
    with st.chat_message("user"):
        st.write("USER QUESTION " + str(i))
    with st.chat_message("assistant"):
        output = make_valid_output()
        output.expert_diagnosis = "DISPLAYED INSIGHT " + str(i) + " — α"
        render_can_bus_analyst(output)
        render_copy_button(key="copy_" + str(i))
st.button("Rerun")
'''.replace("ROOT", repr(str(root))), encoding="utf-8")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, ANALYTICS_ENABLED="false")
    with (tmp_path / "server.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(app),
             "--server.headless=true", f"--server.port={port}",
             "--server.address=127.0.0.1", "--browser.gatherUsageStats=false"],
            env=env, stdout=log, stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with playwright.sync_playwright() as p:
                try:
                    browser = p.chromium.launch(headless=True, channel="msedge")
                except playwright.Error:
                    try:
                        browser = p.chromium.launch(headless=True)
                    except playwright.Error:
                        pytest.skip("Install a Playwright Chromium browser to run clipboard checks")
                context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
                page = context.new_page()
                origin = f"http://127.0.0.1:{port}"
                for attempt in range(60):
                    try:
                        page.goto(origin)
                        break
                    except playwright.Error:
                        time.sleep(.25)
                page.locator("iframe").nth(1).wait_for(timeout=30000)
                assistants = page.locator('[data-testid="stChatMessageContent"]').filter(
                    has=page.locator("iframe")
                )
                for i in range(2):
                    answer = assistants.nth(i)
                    frame = page.frame_locator("iframe").nth(i)
                    before = answer.locator("details").evaluate_all("els => els.map(e => e.open)")
                    frame.get_by_role("button", name="Copy full response").click()
                    frame.get_by_role("status").filter(has_text="Copied!").wait_for()
                    copied = page.evaluate("navigator.clipboard.readText()")
                    assert answer.locator("details").evaluate_all("els => els.map(e => e.open)") == before
                    # Independent reference: native selection after explicitly opening every section.
                    answer.locator("details").evaluate_all("els => els.forEach(e => e.open = true)")
                    inert = answer.locator("[inert]")
                    inert.evaluate_all("els => els.forEach(e => {e.dataset.copyTestInert = 'true'; e.removeAttribute('inert')})")
                    expected = answer.evaluate('''root => {
                        const range = document.createRange();
                        range.selectNodeContents(root);
                        const selected = window.getSelection();
                        selected.removeAllRanges(); selected.addRange(range);
                        const text = selected.toString(); selected.removeAllRanges();
                        return text;
                    }''')
                    answer.locator("details").evaluate_all(
                        "(els, states) => els.forEach((e, n) => e.open = states[n])", before
                    )
                    answer.locator("[data-copy-test-inert]").evaluate_all("els => els.forEach(e => {e.setAttribute('inert', ''); delete e.dataset.copyTestInert})")
                    # Windows clipboard normalizes LF to CRLF, like native copying.
                    assert copied.replace("\r\n", "\n") == expected.replace("\r\n", "\n")
                    assert f"DISPLAYED INSIGHT {i} — α" in copied
                    assert f"DISPLAYED INSIGHT {1-i}" not in copied
                    assert "USER QUESTION" not in copied
                    assert "Key Insight" in copied
                    assert "Expert Diagnosis" not in copied
                    assert "Is Hypothesis" not in copied
                    assert "Engineering response" not in copied
                    assert "personal project by" not in copied
                    assert "Copy full response" not in copied
                    assert "Recommended Tools" in copied
                    assert "Fallback if unavailable" in copied
                    assert "Narrowing Questions" in copied
                    assert "Yes →" in copied
                    assert "Self Evaluation" in copied
                page.get_by_role("button", name="Rerun", exact=True).click()
                frame = page.frame_locator("iframe").nth(0)
                frame.get_by_role("button", name="Copy full response").click()
                page.wait_for_function("async () => (await navigator.clipboard.readText()).includes('DISPLAYED INSIGHT 0')")
                # A denied clipboard must expose exactly the same answer for manual copying.
                frame.locator("body").evaluate('''() => {
                    Object.defineProperty(navigator, "clipboard", {value: {writeText: () => Promise.reject(new Error("denied"))}});
                    document.execCommand = () => false;
                }''')
                frame.get_by_role("button", name="Copy full response").click()
                manual = frame.get_by_role("textbox")
                manual.wait_for(state="visible")
                assert manual.input_value().replace("\r\n", "\n") == page.evaluate("navigator.clipboard.readText()").replace("\r\n", "\n")
                browser.close()
        finally:
            process.terminate()
            process.wait(timeout=15)
