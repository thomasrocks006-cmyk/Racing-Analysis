#!/usr/bin/env node
/**
 * VS Code Copilot Bridge - Access GitHub Copilot via vscode.lm API
 *
 * This script uses the official VS Code Language Model API to access GitHub Copilot.
 * It DOES use your 1500 premium requests from GitHub Copilot Pro Plus!
 *
 * Usage:
 *   node copilot_vscode_bridge.js "Your question here"
 *
 * Or as a server:
 *   node copilot_vscode_bridge.js --server
 */

const vscode = require('vscode');

/**
 * Query GitHub Copilot using vscode.lm API
 * This uses your premium requests!
 */
async function queryCopilot(prompt, systemPrompt = null) {
    try {
        // Select GitHub Copilot model (uses premium requests)
        const [model] = await vscode.lm.selectChatModels({
            vendor: 'copilot',
            family: 'gpt-4o'  // or 'gpt-4', 'o1-preview' depending on what's available
        });

        if (!model) {
            return {
                success: false,
                error: 'copilot_not_available',
                message: 'GitHub Copilot model not available. Check your subscription and consent.'
            };
        }

        // Build messages
        const messages = [];
        if (systemPrompt) {
            messages.push(vscode.LanguageModelChatMessage.User(systemPrompt));
        }
        messages.push(vscode.LanguageModelChatMessage.User(prompt));

        // Send request to Copilot (uses 1 premium request)
        const response = await model.sendRequest(messages, {}, new vscode.CancellationTokenSource().token);

        // Collect response
        let content = '';
        for await (const chunk of response.text) {
            content += chunk;
        }

        return {
            success: true,
            content: content.trim(),
            model: model.id,
            vendor: model.vendor,
            family: model.family,
            uses_premium_requests: true
        };

    } catch (err) {
        if (err instanceof vscode.LanguageModelError) {
            return {
                success: false,
                error: err.code,
                message: err.message,
                cause: err.cause?.message
            };
        }

        return {
            success: false,
            error: 'unknown_error',
            message: err.message || String(err)
        };
    }
}

/**
 * Run as CLI
 */
async function cli() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.error('Usage: node copilot_vscode_bridge.js "Your question"');
        process.exit(1);
    }

    const prompt = args.join(' ');
    const result = await queryCopilot(prompt);

    console.log(JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
}

/**
 * Run as HTTP server for Python to call
 */
async function server() {
    const http = require('http');
    const PORT = 3737;

    const server = http.createServer(async (req, res) => {
        if (req.method === 'POST' && req.url === '/copilot/chat') {
            let body = '';

            req.on('data', chunk => {
                body += chunk.toString();
            });

            req.on('end', async () => {
                try {
                    const { prompt, system_prompt } = JSON.parse(body);
                    const result = await queryCopilot(prompt, system_prompt);

                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify(result));
                } catch (error) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        success: false,
                        error: 'invalid_request',
                        message: error.message
                    }));
                }
            });
        } else if (req.method === 'GET' && req.url === '/health') {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'healthy', api: 'vscode.lm' }));
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
    });

    server.listen(PORT, () => {
        console.log(`GitHub Copilot Bridge Server running on http://localhost:${PORT}`);
        console.log(`Send POST to /copilot/chat with {"prompt": "...", "system_prompt": "..."}`);
    });
}

// Check if running as server or CLI
if (process.argv.includes('--server')) {
    server();
} else {
    cli();
}
