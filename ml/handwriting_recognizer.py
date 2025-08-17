import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image

class HandwritingRecognizer:
    def __init__(self):
        # 事前学習済みモデルとトークナイザをロード
        model_name = "nlpconnect/vit-gpt2-image-captioning"
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def recognize(self, image_path):
        # 画像をロードして前処理
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.feature_extractor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        # 推論を実行
        output_ids = self.model.generate(pixel_values, max_length=16, num_beams=4)
        
        # テキストにデコード
        generated_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return generated_text