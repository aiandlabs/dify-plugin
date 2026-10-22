# ai& for Dify

Dify で ai& のオープンウェイトモデル（DeepSeek、Qwen、GLM、Kimi、Gemma、gpt-oss など）を利用できます。`https://api.aiand.com/v1` の OpenAI 互換 API で提供しています。

## セットアップ

1. [ai& コンソール](https://console.aiand.com)で API キーを作成します。キーは `sk-` で始まります。
2. Dify で **設定 → モデルプロバイダー** を開き、**ai&** の **セットアップ** をクリックします。
3. API キーを貼り付けて保存します。Dify が短いテストリクエストでキーを確認します。

## 使い方

セットアップ後、ai& の現行チャットモデルをすべて利用できます。LLM ノード、エージェント、チャットボットで選択してください。

- **ツール呼び出し**：すべてのモデルで利用でき、並列・ストリーミングのツール呼び出しにも対応しています。
- **画像入力**：vision 対応モデルで利用できます。
- **推論の強度**：回答前にモデルが推論する量を選べます。各モデルは対応する段階のみを表示します。`none` は対応モデルで推論をオフにします。
- **構造化出力**：一覧のモデルでは、レスポンス形式の設定から利用できます。

一覧にないモデルを使う場合は **モデルを追加** を選び、`https://api.aiand.com/v1/models` に記載のモデル ID を入力してください。

## 接続要件

- ai& の API キー
- Dify から `api.aiand.com` への HTTPS 通信

## 料金

リクエストは ai& アカウントに、[ai& の料金ページ](https://docs.aiand.com/models/pricing/)に掲載の料金で課金されます。Dify にも同じトークン単価が表示されます。

## プライバシー

回答の生成のため、プロンプトと応答は ai& に送信されます。[PRIVACY.md](https://github.com/aiandlabs/dify-plugin/blob/main/PRIVACY.md) と [ai& のプライバシーポリシー](https://aiand.com/privacy)をご覧ください。

## サポート

- 連絡先：support@aiand.com
- ソース：https://github.com/aiandlabs/dify-plugin
