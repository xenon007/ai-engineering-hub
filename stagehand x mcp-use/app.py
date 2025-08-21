import os
import json
import asyncio
import base64
import time
import warnings

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use

from styles import inject_css

warnings.filterwarnings("ignore")
load_dotenv()
if os.getenv("DEBUG_MCP", "0") == "1":
    mcp_use.set_debug(1)

st.set_page_config(page_title="Stagehand × mcp-use", page_icon="🕹️", layout="wide")
inject_css()

SAMPLE_CONFIG_STR = """{
  "mcpServers": {
    "browserbase": {
      "command": "npx",
      "args": [
        "-y",
        "@browserbasehq/mcp-server-browserbase",
        "--modelName", "ollama/llama3.2:8b"
      ],
      "env": {
        "BROWSERBASE_API_KEY": "<your-browserbase-api-key>",
        "BROWSERBASE_PROJECT_ID": "<your-browserbase-project-id>",
        "OLLAMA_HOST": "http://127.0.0.1:11434"
      }
    }
  }
}"""

st.session_state.setdefault("client", None)
st.session_state.setdefault("agent", None)
st.session_state.setdefault("activated", False)
st.session_state.setdefault("tools", [])
st.session_state.setdefault("config_json", SAMPLE_CONFIG_STR)
st.session_state.setdefault("messages", [])  # [{role, content}]

def _read_config_file() -> dict:
    cfg_path = os.getenv("MCP_CONFIG", "mcp-config.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def _activate(cfg_dict: dict):
    client = MCPClient.from_dict(cfg_dict)
    await client.create_all_sessions()

    tools = set()
    for name in (cfg_dict.get("mcpServers") or {}):
        try:
            session = client.get_session(name)
            for t in await session.list_tools():
                tools.add(str(getattr(t, "name", None) or getattr(t, "tool", None) or "unknown"))
        except Exception as e:
            st.sidebar.warning(f"Could not list tools for '{name}': {e}")

    llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)
    agent = MCPAgent(
        llm=llm,
        client=client,
        system_prompt=(
            "When using Browserbase tools, reuse an existing session if available. "
            "If navigation fails due to a missing session or 429, call `browserbase_session_create` once, then retry."
        ),
        max_steps=int(os.getenv("MAX_STEPS", "20")),
        memory_enabled=True,
    )
    return client, sorted(tools), agent



def handle_load_sample():
    st.session_state.config_json = SAMPLE_CONFIG_STR

def handle_activate():
    if st.session_state.client is not None:
        try:
            asyncio.run(st.session_state.client.close_all_sessions())
        except Exception:
            pass
    try:
        cfg = _read_config_file()
        client, tools, agent = asyncio.run(_activate(cfg))
        st.session_state.client = client
        st.session_state.tools = tools
        st.session_state.agent = agent
        st.session_state.activated = True
        st.sidebar.success(f"Activated with config file: {os.getenv('MCP_CONFIG', 'mcp-config.json')}")
    except Exception as e:
        st.session_state.client = None
        st.session_state.tools = []
        st.session_state.agent = None
        st.session_state.activated = False
        st.sidebar.error(f"Failed to activate configuration: {e}")

def handle_clear():
    if st.session_state.client is not None:
        try:
            asyncio.run(st.session_state.client.close_all_sessions())
        except Exception:
            pass
    st.session_state.update(client=None, agent=None, tools=[], activated=False, messages=[])

def _file_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _render_hero():
    try:
        sh_b64 = _file_b64(os.path.join("assets", "stagehand.png"))
        mu_b64 = _file_b64(os.path.join("assets", "mcp-use.png"))
    except Exception:
        sh_b64 = mu_b64 = ""
    st.markdown(
        f"""
        <div class="hero">
          <h1>Stagehand × mcp-use</h1>
          <div class="logo-row">
            <img src="data:image/png;base64,{sh_b64}" alt="Stagehand" />
            <img src="data:image/png;base64,{mu_b64}" alt="mcp-use" />
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _looks_transient(err_msg: str) -> bool:
    if not err_msg:
        return False
    t = err_msg.lower()
    return ("no session found" in t) or ("429" in t) or ("rate limit" in t) or ("failed to create browserbase session" in t)

def run_agent_with_retry(agent, prompt, max_retries: int = 1, backoff_sec: float = 2.5) -> str:
    try:
        return asyncio.run(agent.run(prompt)) or "(no response)"
    except Exception as e:
        first = str(e)
        if _looks_transient(first) and max_retries > 0:
            time.sleep(backoff_sec)
            try:
                return asyncio.run(agent.run(prompt)) or "(no response)"
            except Exception as e2:
                return f"⚠️ MCP/Agent error (after retry): {e2}"
        return f"⚠️ MCP/Agent error: {first}"

with st.sidebar:
    st.markdown("## MCP Configuration")
    st.caption("Enter MCP Configuration (JSON)")
    st.text_area("Enter MCP Configuration (JSON)", key="config_json", height=260, label_visibility="collapsed")
    st.button("Load Sample Config", on_click=handle_load_sample)
    st.button("Activate Configuration", on_click=handle_activate)
    st.button("Clear Chat & Config", on_click=handle_clear)

    st.divider()
    if not st.session_state.activated:
        st.warning("⚠️ Configuration not activated")
    else:
        st.success("✅ MCP Client Active")
        st.success("✅ Agent Ready")
        st.markdown("**Available MCP tools:**")
        if st.session_state.tools:
            for t in st.session_state.tools:
                st.markdown(f"- {t}")
        else:
            st.caption("• (no tools found)")

_render_hero()

# History (static)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Current turn with opaque placeholder to avoid shadow
user_input = st.chat_input("Ask Stagehand via MCP…")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        ph = st.empty()
        ph.markdown('<div class="bubble-opaque">&nbsp;</div>', unsafe_allow_html=True)
        if not (st.session_state.activated and st.session_state.agent):
            assistant_text = "Please activate the configuration first."
        else:
            with st.spinner("Running agent..."):
                assistant_text = run_agent_with_retry(st.session_state.agent, user_input)
        ph.markdown(assistant_text, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
