# AI Code Assistant

A modern, intelligent code completion and debugging assistant built with Streamlit, focused on TypeScript development. Powered by OpenAI's GPT models with streaming responses.

## 🚀 Features

- **Code Editor**: Multi-file TypeScript editor with syntax highlighting
- **Real-time AI Assistance**: Code completion, debugging, refactoring, and explanations
- **Smart Debugging**: Paste errors/stacktraces for root-cause analysis and fix suggestions
- **Session History**: Track your interactions with collapsible timeline
- **File Management**: Upload/download TypeScript projects as ZIP files
- **VSCode Integration**: Generate extension stubs and integration helpers
- **Modern UI**: Dark theme with CSS animations and responsive design

## 📋 Requirements

- Python 3.8+
- Modern web browser

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app_main.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 Quick Start Demo

1. **Start the app** with the command above
2. **Load sample code**: The app starts with a sample TypeScript UserService class
3. **Try debugging**: Click "🐛 Debug" and ask about the missing validation bug
4. **Test completion**: Click "✨ Complete" and ask to add error handling
5. **Refactor code**: Click "🔧 Refactor" to improve the code structure
6. **Explain code**: Click "💡 Explain" for simple explanations

## 📁 Project Structure

```
ai-code-assistant/
├── app_main.py          # Main Streamlit application
├── openai_client.py     # OpenAI API client with streaming
├── styles.css           # Modern CSS styling
├── vscode_api.py        # VSCode API integration stub
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

### Model Settings (Available in Sidebar)

- **Model**: Choose between gpt-4o-mini, gpt-4, gpt-3.5-turbo
- **Max Tokens**: Control response length (100-2000)
- **Temperature**: Adjust creativity (0.0-1.0)
- **Streaming**: Enable/disable real-time responses

## 🌐 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

## 🔌 VSCode Integration

### Extension Stub Generation
1. Click "📋 Generate VSCode Extension Stub" in the app
2. Download the generated JavaScript file
3. Place in `.vscode/extensions/ai-assistant/`

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Slow responses**
- Check internet connection
- Try a different OpenAI model
- Reduce max_tokens setting

---

**Built with ❤️ using Streamlit and OpenAI**