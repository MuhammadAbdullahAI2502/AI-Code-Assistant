"""
VSCode API Integration Stub
This module provides documented stubs for VSCode API integration.
"""

import json
from typing import Dict, Any

def generate_extension_manifest() -> Dict[str, Any]:
    """Generate VSCode extension package.json manifest."""
    return {
        "name": "ai-code-assistant",
        "displayName": "AI Code Assistant",
        "description": "Intelligent code completion and debugging assistant",
        "version": "1.0.0",
        "engines": {
            "vscode": "^1.74.0"
        },
        "categories": ["Other"],
        "activationEvents": [
            "onLanguage:typescript",
            "onLanguage:javascript"
        ],
        "main": "./out/extension.js",
        "contributes": {
            "commands": [
                {
                    "command": "ai-assistant.complete",
                    "title": "AI Complete Code"
                },
                {
                    "command": "ai-assistant.debug",
                    "title": "AI Debug Code"
                }
            ],
            "keybindings": [
                {
                    "command": "ai-assistant.complete",
                    "key": "ctrl+alt+space",
                    "when": "editorTextFocus"
                }
            ]
        }
    }

def generate_extension_code() -> str:
    """Generate VSCode extension TypeScript code."""
    return '''
const vscode = require('vscode');

function activate(context) {
    let disposable = vscode.commands.registerCommand('ai-assistant.complete', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const selection = editor.selection;
            const text = editor.document.getText(selection);
            
            // Call your AI API here
            const response = await fetch('http://localhost:8501/api/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: text })
            });
            
            const result = await response.text();
            editor.edit(editBuilder => {
                editBuilder.replace(selection, result);
            });
        }
    });
    
    context.subscriptions.push(disposable);
}

exports.activate = activate;
'''