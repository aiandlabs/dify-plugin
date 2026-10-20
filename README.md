# ai& for Dify

Use ai& open-weight models in Dify: DeepSeek, Qwen, GLM, Kimi, Gemma, gpt-oss and more, served through an OpenAI-compatible API at `https://api.aiand.com/v1`.

日本語版は [readme/README_ja_JP.md](readme/README_ja_JP.md) をご覧ください。

## Setup

1. Create an API key in the [ai& console](https://console.aiand.com). Keys start with `sk-`.
2. In Dify, open **Settings → Model Provider**, find **ai&** and click **Setup**.
3. Paste your API key and save. Dify checks the key with a short test request.

## Usage

All current ai& chat models are available after setup. Pick one in any LLM node, agent, or chatbot.

- **Tool calling** works on every model, including parallel and streamed tool calls.
- **Image input** works on models marked with vision.
- **Reasoning effort** lets you choose how much a model reasons before answering. Each model lists only the levels it supports. `none` turns reasoning off where the model allows it.
- **Structured output** is available through the response format setting.

To use a model that is not listed yet, choose **Add Model** and enter its ID from `https://api.aiand.com/v1/models`.

## Requirements

- An ai& API key.
- Outbound HTTPS access from your Dify instance to `api.aiand.com`.

## Pricing

Requests are billed to your ai& account at the prices published on the [ai& pricing page](https://docs.aiand.com/models/pricing/). Dify shows the same per-token prices.

## Privacy

Prompts and responses are sent to ai& to generate replies. See the [ai& privacy policy](https://aiand.com/privacy).

## Support

- Contact: support@aiand.com
- Source: https://github.com/aiandlabs/dify-plugin
