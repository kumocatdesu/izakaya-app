# 居酒屋Handyアプリ

## 概要
このアプリケーションは、タブレット端末で手書きされた注文をAIが認識し、メニューを自動的に注文するシステムです。

## 機能
- **手書き文字認識**: 注文用紙に手書きされたメニュー名をAIが認識します。
- **メニュー推薦**: 認識されたメニューに基づいて、AIが相性の良い料理を推薦します。
- **データベース連携**: メニュー情報や注文履歴をデータベースで管理します。

## 開発環境
- Python 3.x
- PyQt6
- SQLite3
- PyTorch
- Transformers (Hugging Face)
- Pillow

## 使い方
1. 必要なPythonパッケージをインストールします。
   ```bash
   pip install PyQt6 sqlite3 Pillow torch transformers