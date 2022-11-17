import io
import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from resnet18 import ResNet
from flask import Flask, jsonify, request, render_template
from PIL import Image

app = Flask(__name__)

def ResNet18(img_channels=3, num_classes=1000):
    return ResNet(18, Block, img_channels, num_classes)

# Modelling Task
model = ResNet18(3, 3)
num_inftr = model.fc.in_features
model.fc = nn.Linear(num_inftr, 4)
model = torch.load('model.pth')
model.eval()

class_names = ['less_damage', 'not_damage', 'severly_damage']

def transform_image(image_bytes):
	data_transforms = transforms.Compose([
        transforms.Resize((224, 224)), 
        transforms.RandomHorizontalFlip(), 
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

	image = Image.open(io.BytesIO(image_bytes))
	return data_transforms(image).unsqueeze(0)

def get_prediction(image_bytes):
	tensor = transform_image(image_bytes=image_bytes)
	outputs = model.forward(tensor)
	confidence, prediction = torch.max(outputs, 1)
	print("confidence:", confidence)
	return class_names[prediction]

details = {
	"less_damage": "Base on this model this phone screen is less damage",
	"not_damage": "It's most likely this phone is not damage at all :D, Correct me if I am wrong ",
	"severly_damage": "Holy Molly, I feel like this phone screen is really damage, I highly suggest you to find the nearest phone repair, to get a replacement",
}

@app.route('/about')
def about():
    return render_template('about.html')

# Treat the web process
@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files.get('file')
		if not file:
			return
		img_bytes = file.read()
		prediction_name = get_prediction(img_bytes)
		print("predicted as: ", prediction_name)
		return render_template('result.html', name=prediction_name.lower(), description=details[prediction_name])

	return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, debug=True)
