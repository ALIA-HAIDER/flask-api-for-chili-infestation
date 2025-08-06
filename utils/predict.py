import torch
from utils.model_loader import transform_image

def predict_single(image_path, model, class_names):
    tensor = transform_image(image_path)
    with torch.no_grad():
        outputs = model(tensor)
        _, predicted = torch.max(outputs, 1)
    return class_names[predicted.item()]

def predict_batch(image_paths, model, class_names):
    batch = torch.cat([transform_image(path) for path in image_paths])
    with torch.no_grad():
        outputs = model(batch)
        _, predicted = torch.max(outputs, 1)
    return {
        os.path.basename(path): class_names[p.item()] 
        for path, p in zip(image_paths, predicted)
    }
