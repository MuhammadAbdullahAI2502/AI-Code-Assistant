import streamlit as st
import asyncio
import json
import zipfile
import io
import os
from datetime import datetime
from typing import Dict, List, Optional
import base64
from openai_client import OpenAIClient

# Page config
st.set_page_config(
    page_title="AI Code Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    try:
        with open("styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline CSS
        st.markdown("""
        <style>
        .stApp { background: #0f172a; color: #f8fafc; }
        .header { 
            display: flex; justify-content: space-between; align-items: center;
            padding: 1rem 2rem; background: #1e293b; border-radius: 0.5rem;
            margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        .header h1 { 
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 0; font-size: 2rem; font-weight: 700;
        }
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white; border: none; border-radius: 0.5rem;
            padding: 0.5rem 1rem; font-weight: 500; transition: all 0.2s ease;
        }
        .stButton > button:hover { transform: translateY(-1px); }
        .download-btn {
            display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white; padding: 0.5rem 1rem; border-radius: 0.5rem;
            text-decoration: none; font-weight: 500; transition: all 0.2s ease;
        }
        .download-btn:hover { transform: translateY(-1px); text-decoration: none; color: white; }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "files" not in st.session_state:
        st.session_state.files = {"main.ts": """// Sample TypeScript code
interface User {
    id: number;
    name: string;
    email: string;
}

class UserService {
    private users: User[] = [];
    
    addUser(user: User): void {
        this.users.push(user);
    }
    
    getUserById(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }
    
    // Bug: missing validation
    updateUser(id: number, updates: Partial<User>): boolean {
        const user = this.getUserById(id);
        if (user) {
            Object.assign(user, updates);
            return true;
        }
        return false;
    }
}"""}
    
    if "active_file" not in st.session_state:
        st.session_state.active_file = "main.ts"
    
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if "openai_client" not in st.session_state:
        api_key = "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"
        st.session_state.openai_client = OpenAIClient(api_key)

def add_to_history(action: str, input_text: str, output_text: str):
    st.session_state.history.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "input": input_text,
        "output": output_text
    })
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[-20:]

def create_download_link(content: str, filename: str, mime_type: str = "text/plain"):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}" class="download-btn">📥 Download {filename}</a>'

def create_project_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in st.session_state.files.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

async def get_completion(prompt: str, code: str, action: str):
    if not st.session_state.openai_client:
        return "❌ OpenAI API key not configured."
    
    try:
        system_prompts = {
            "complete": "You are a TypeScript code completion assistant. Provide only the completion for the given code context.",
            "debug": "You are a debugging expert. Analyze the error and provide step-by-step fix suggestions with code patches.",
            "refactor": "You are a code refactoring expert. Improve the code following best practices and explain changes.",
            "explain": "You are a code explanation expert. Explain the code in simple, clear terms."
        }
        
        system_prompt = system_prompts.get(action, system_prompts["complete"])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Code:\n```typescript\n{code}\n```\n\nRequest: {prompt}"}
        ]
        
        response = await st.session_state.openai_client.get_completion(
            messages=messages,
            model=st.session_state.get("model", "gpt-4o-mini"),
            max_tokens=st.session_state.get("max_tokens", 1000),
            temperature=st.session_state.get("temperature", 0.7),
            stream=st.session_state.get("streaming", True)
        )
        
        return response
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    load_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="header">
        <h1>🤖 AI Code Assistant</h1>
        <div class="status">
            <span>Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # API Status
        if st.session_state.openai_client:
            st.success("✅ OpenAI API Connected")
        else:
            st.error("❌ OpenAI API Key Missing")
            st.info("API key hardcoded in app")
        
        # Model settings
        st.session_state.model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            index=0
        )
        
        st.session_state.max_tokens = st.slider("Max Tokens", 100, 2000, 1000)
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        st.session_state.streaming = st.checkbox("Streaming", value=True)
        
        # File upload
        st.markdown("### 📁 Project Management")
        uploaded_file = st.file_uploader("Upload TypeScript files", type=['ts', 'js', 'zip'])
        
        if uploaded_file:
            if uploaded_file.name.endswith('.zip'):
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith(('.ts', '.js')):
                            content = zip_ref.read(file_info.filename).decode('utf-8')
                            st.session_state.files[file_info.filename] = content
                st.success(f"Loaded {len(st.session_state.files)} files")
            else:
                content = uploaded_file.read().decode('utf-8')
                st.session_state.files[uploaded_file.name] = content
                st.session_state.active_file = uploaded_file.name
                st.success(f"Loaded {uploaded_file.name}")
        
        # Download project
        if st.button("📦 Download Project"):
            zip_data = create_project_zip()
            st.download_button(
                label="💾 Download ZIP",
                data=zip_data,
                file_name="typescript_project.zip",
                mime="application/zip"
            )
    
    # Main layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 📝 Code Editor")
        
        # File selector
        current_file = st.selectbox("Select File", list(st.session_state.files.keys()))
        st.session_state.active_file = current_file
        
        # Code editor
        code = st.text_area(
            f"Editing: {current_file}",
            value=st.session_state.files[current_file],
            height=400,
            key=f"editor_{current_file}"
        )
        
        if code != st.session_state.files[current_file]:
            st.session_state.files[current_file] = code
        
        # New file creation
        with st.expander("➕ Create New File"):
            new_filename = st.text_input("New file name", placeholder="example.ts")
            if st.button("Create File") and new_filename:
                st.session_state.files[new_filename] = "// New TypeScript file\n"
                st.session_state.active_file = new_filename
                st.rerun()
    
    with col2:
        st.markdown("### 🤖 AI Assistant")
        
        # Quick actions
        st.markdown("#### Quick Actions")
        action_cols = st.columns(2)
        
        with action_cols[0]:
            if st.button("🔧 Refactor", use_container_width=True):
                st.session_state.action = "refactor"
            if st.button("🐛 Debug", use_container_width=True):
                st.session_state.action = "debug"
        
        with action_cols[1]:
            if st.button("💡 Explain", use_container_width=True):
                st.session_state.action = "explain"
            if st.button("✨ Complete", use_container_width=True):
                st.session_state.action = "complete"
        
        # Custom prompt
        prompt = st.text_area(
            "Custom request:",
            placeholder="Ask me anything about your code...",
            height=100
        )
        
        if st.button("🚀 Execute", use_container_width=True, type="primary"):
            if prompt and st.session_state.active_file in st.session_state.files:
                with st.spinner("🤔 Thinking..."):
                    current_code = st.session_state.files[st.session_state.active_file]
                    action = getattr(st.session_state, 'action', 'complete')
                    
                    # Run async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        get_completion(prompt, current_code, action)
                    )
                    loop.close()
                    
                    add_to_history(action, prompt, response)
                    
                    st.markdown("#### 📋 Response")
                    st.markdown(response)
        
        # Session History
        if st.session_state.history:
            with st.expander("📚 Session History", expanded=False):
                for item in reversed(st.session_state.history[-5:]):
                    st.markdown(f"""
                    **{item['action'].title()}** - {item['timestamp'][:19]}
                    
                    *Input:* {item['input'][:100]}...
                    
                    *Output:* {item['output'][:200]}...
                    
                    ---
                    """)
        
        # VSCode Integration
        st.markdown("#### 🔗 VSCode Integration")
        if st.button("📋 Generate VSCode Extension Stub"):
            from vscode_api import generate_extension_code
            vscode_stub = generate_extension_code()
            
            st.code(vscode_stub, language='javascript')
            st.markdown(create_download_link(vscode_stub, "vscode-extension.js", "text/javascript"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()