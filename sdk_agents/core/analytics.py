"""
Anonymous session analytics — GDPR-safe, CSV-backed, feature-flagged.

GDPR posture:
  - No cookies written (server-side CSV only, nothing in the browser)
  - No personal data: IP never stored, queries truncated to 300 chars
  - No external calls unless GA4/Plausible wired up in Tier B/C
  - session_id is a random UUID with no link to any identity

Feature flag:
  Set ANALYTICS_ENABLED=false in .env or environment to disable entirely.
  Every public function returns a safe default on any error —
  analytics can never break the app under any circumstance.

Admin dashboard:
  Accessible via ?admin=true&key=<ANALYTICS_SECRET>
  Set ANALYTICS_SECRET in .env / Streamlit Cloud secrets.
  Defaults to "admin" for local dev only — always override in production.

Tier B/C upgrade path (5-line future hook):
  Set GA_MEASUREMENT_ID=G-XXXXXXXXXX to enable GA4 cookieless events.
  The session/ref/duration infrastructure is already in place.
"""

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────────

ANALYTICS_ENABLED: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
ANALYTICS_SECRET: str = os.getenv("ANALYTICS_SECRET", "admin")
GA_MEASUREMENT_ID: str = os.getenv("GA_MEASUREMENT_ID", "")  # Tier B: set G-XXXXXXXXXX

_LOGS_DIR = Path(__file__).parents[1] / "logs"
_CSV_PATH = _LOGS_DIR / "analytics.csv"
_CSV_FIELDS = ["session_id", "timestamp", "ref", "event_name", "details", "duration_sec"]


# ── Public API ─────────────────────────────────────────────────────────────────

def init_analytics() -> None:
    """
    Call once after st.set_page_config(). Idempotent — guarded by session_state
    so reruns (which re-execute the full script) are safe.
    Initialises session_id, start timestamp, and ?ref= capture.
    Fires session_start event exactly once per browser session.
    """
    try:
        if not ANALYTICS_ENABLED:
            return
        if "_analytics_session_id" in st.session_state:
            return  # already initialised this session
        st.session_state["_analytics_session_id"] = str(uuid4())
        st.session_state["_analytics_start"] = datetime.now(timezone.utc)
        st.session_state["_analytics_ref"] = st.query_params.get("ref", "unknown")
        st.session_state["_analytics_prev_agent"] = "__initial__"
        _write_row("session_start", {})
    except Exception:
        pass  # analytics never breaks the app


def track_event(event_name: str, details: dict | None = None) -> None:
    """
    Track any named event. Silent no-op when:
      - ANALYTICS_ENABLED=false
      - session was never initialised (init_analytics failed silently)
      - CSV write fails for any reason
    Never raises — the calling code in app.py needs no try/except.
    """
    try:
        if not ANALYTICS_ENABLED:
            return
        if "_analytics_session_id" not in st.session_state:
            return
        _write_row(event_name, details or {})
    except Exception:
        pass


def track_agent_selected(selected_agent: str | None) -> None:
    """
    Fire agent_selected only when the dropdown value actually changes.
    Prevents duplicate events on every Streamlit rerun (the script re-executes
    top-to-bottom on every user interaction, not just on dropdown changes).

    Call this inside `if page == "Try the Agent":` only — after selected_agent
    is resolved — so selected_agent is always in scope.

    None is normalised to "auto" to avoid dict key inconsistencies.
    """
    try:
        if not ANALYTICS_ENABLED:
            return
        label = selected_agent or "auto"  # normalise None → "auto"
        if label == st.session_state.get("_analytics_prev_agent", "__initial__"):
            return  # no change since last rerun — skip
        st.session_state["_analytics_prev_agent"] = label
        track_event("agent_selected", {"agent": label})
    except Exception:
        pass


def is_admin_request() -> bool:
    """
    Returns True when both ?admin=true and ?key=<ANALYTICS_SECRET> are present.
    Returns False on any error so the normal app always loads as a fallback.
    """
    try:
        return (
            st.query_params.get("admin") == "true"
            and st.query_params.get("key") == ANALYTICS_SECRET
        )
    except Exception:
        return False


def render_analytics_dashboard() -> None:
    """
    Render the full admin-only analytics dashboard.
    Called from app.py immediately after init_analytics() when is_admin_request()
    is True — followed by st.stop() so the normal app never renders.

    Note: st.set_page_config() is NOT called here — already called in app.py
    before this function is reached.
    """
    try:
        import pandas as pd  # noqa: F401 — validates pandas is available

        st.title("Usage Analytics")
        st.caption("Anonymous sessions only — no personal data stored.")

        # Warn when running with the default secret key
        if ANALYTICS_SECRET == "admin":
            st.warning(
                "**ANALYTICS_SECRET is set to the default value 'admin'.** "
                "Override this in your .env file or Streamlit Cloud secrets before sharing the URL."
            )

        df = _load_df()
        if df is None or df.empty:
            st.info("No analytics data yet. Share the app link to start collecting sessions.")
            return

        # Convert UTC timestamps to Germany time (Europe/Berlin) for display
        try:
            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert("Europe/Berlin")
        except Exception:
            pass  # already tz-aware or conversion failed — show as-is

        # ── Bot filter ─────────────────────────────────────────────────────────
        # A session is a likely bot only if it lasted under 5 seconds AND
        # submitted no query. HR/non-technical visitors who read the About page
        # spend 30–60 seconds and are counted as real sessions.
        show_bots = st.checkbox(
            "Include likely bots (< 5s session with no submitted query)", value=False
        )
        if not show_bots:
            max_duration = df.groupby("session_id")["duration_sec"].max()
            has_input = df[df["event_name"] == "input_submitted"]["session_id"].unique()
            bot_sessions = max_duration[
                (max_duration < 5) & (~max_duration.index.isin(has_input))
            ].index
            df = df[~df["session_id"].isin(bot_sessions)]

        if df.empty:
            st.info("No real user sessions yet (all current sessions filtered as bots).")
            return

        # ── Top-line metrics ───────────────────────────────────────────────────
        total_sessions = df["session_id"].nunique()
        total_queries = int(len(df[df["event_name"] == "input_submitted"]))
        durations = df.groupby("session_id")["duration_sec"].max()
        avg_dur = round(float(durations.mean()), 1) if not durations.empty else 0.0
        max_dur = round(float(durations.max()), 1) if not durations.empty else 0.0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Sessions",  total_sessions)
        c2.metric("Total Queries",   total_queries)
        c3.metric("Avg Duration",    f"{avg_dur}s")
        c4.metric("Max Duration",    f"{max_dur}s")

        st.markdown("---")
        col_l, col_r = st.columns(2)

        # ── Top agents used ────────────────────────────────────────────────────
        with col_l:
            st.subheader("Top Agents Used")
            inputs = df[df["event_name"] == "input_submitted"].copy()
            if not inputs.empty:
                inputs["agent"] = inputs["details"].apply(
                    lambda x: _parse_detail(x, "agent", "unknown")
                )
                counts = (
                    inputs["agent"]
                    .value_counts()
                    .rename_axis("agent")
                    .reset_index(name="queries")
                )
                st.bar_chart(counts.set_index("agent"))
            else:
                st.info("No queries yet.")

        # ── Referral sources ───────────────────────────────────────────────────
        with col_r:
            st.subheader("Referral Sources")
            ref_counts = (
                df.groupby("ref")["session_id"]
                .nunique()
                .rename_axis("ref")
                .reset_index(name="sessions")
                .sort_values("sessions", ascending=False)
            )
            st.bar_chart(ref_counts.set_index("ref"))

        st.markdown("---")

        # ── Sessions per day ───────────────────────────────────────────────────
        st.subheader("Sessions Per Day")
        starts = df[df["event_name"] == "session_start"].copy()
        if not starts.empty:
            starts["date"] = starts["timestamp"].dt.date
            daily = (
                starts.groupby("date")["session_id"]
                .nunique()
                .rename_axis("date")
                .reset_index(name="sessions")
            )
            st.bar_chart(daily.set_index("date"))

        st.markdown("---")

        # ── Last 20 queries ────────────────────────────────────────────────────
        st.subheader("Last 20 Queries")
        inputs = df[df["event_name"] == "input_submitted"].copy()
        if not inputs.empty:
            inputs["agent"] = inputs["details"].apply(
                lambda x: _parse_detail(x, "agent", "")
            )
            inputs["query"] = inputs["details"].apply(
                lambda x: _parse_detail(x, "query", "")
            )
            recent = inputs.sort_values("timestamp", ascending=False).head(20)
            st.dataframe(
                recent[["timestamp", "session_id", "ref", "agent", "query"]]
                .reset_index(drop=True),
                use_container_width=True,
            )
        else:
            st.info("No queries yet.")

    except Exception as exc:
        # Dashboard errors are shown inside the admin page — normal app is never affected
        # because st.stop() is called in app.py after render_analytics_dashboard()
        st.error(f"Dashboard error: {exc}")


# ── Private helpers ─────────────────────────────────────────────────────────────

def _write_row(event_name: str, details: dict) -> None:
    """Append one row to analytics.csv. Silently swallows all exceptions."""
    try:
        _LOGS_DIR.mkdir(exist_ok=True)
        write_header = not _CSV_PATH.exists()
        with _CSV_PATH.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow({
                "session_id":   st.session_state.get("_analytics_session_id", ""),
                "timestamp":    datetime.now(timezone.utc).isoformat(),
                "ref":          st.session_state.get("_analytics_ref", "unknown"),
                "event_name":   event_name,
                "details":      json.dumps(details),
                "duration_sec": _duration_sec(),
            })
    except Exception:
        pass


def _duration_sec() -> float:
    """Seconds elapsed since session start. Returns 0.0 on any error."""
    try:
        start = st.session_state.get("_analytics_start")
        if start is None:
            return 0.0
        return round((datetime.now(timezone.utc) - start).total_seconds(), 1)
    except Exception:
        return 0.0


def _load_df():
    """Read analytics.csv into a DataFrame. Returns None if unavailable."""
    try:
        import pandas as pd
        if not _CSV_PATH.exists():
            return None
        return pd.read_csv(_CSV_PATH, parse_dates=["timestamp"])
    except Exception:
        return None


def _parse_detail(raw: str, key: str, default: str) -> str:
    """Safely extract a key from a JSON details string."""
    try:
        return json.loads(raw).get(key, default)
    except Exception:
        return default
