import torch
from torchvision import transforms
from PIL import Image

def load_model(model_path):
    model = torch.load(model_path, map_location=torch.device('cpu'))
    model.eval()
    
    # Define class names (in correct order)
    class_names = ['Aphids', 'Healthy', 'mites+thrips']
    return model, class_names

def transform_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # adjust to your model's input size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],  # ImageNet normalization
                             std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)  # Add batch dimension
