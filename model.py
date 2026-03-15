from transformers import AutoImageProcessor, AutoModelForImageClassification, ViTImageProcessor
from PIL import Image
import torch

class aiModel:
    processor = None
    model = None
    def __init__(self):
        # Load the specific processor class for ViT models
        processor = ViTImageProcessor.from_pretrained("Abuzaid01/asl-sign-language-classifier")
        model = AutoModelForImageClassification.from_pretrained("Abuzaid01/asl-sign-language-classifier")


    def predict(imageFile):
        # Load an image
        image = Image.open(imageFile)

        # Preprocess
        inputs = processor(images=image, return_tensors="pt")

        # Predict
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = logits.argmax(-1).item()

        predicted_class = model.config.id2label[predicted_class]
        print("Predicted class:", predicted_class)

        return predicted_class
    
if __name__ == "__main__":
    model = aiModel
    print("model ", model)
    model.predict("test")