class RecommendationEngine:
    def recommend_items(self, recognized_text):
        # ここに推薦ロジックを実装します
        # 例：キーワードに基づいてメニューを推薦
        if "ビール" in recognized_text:
            return ["枝豆", "唐揚げ", "ポテトサラダ"]
        elif "日本酒" in recognized_text:
            return ["刺身", "焼き魚", "揚げ出し豆腐"]
        elif "焼酎" in recognized_text:
            return ["もつ煮", "きゅうりの一本漬け", "チャンジャ"]
        else:
            return ["おすすめはありません"]