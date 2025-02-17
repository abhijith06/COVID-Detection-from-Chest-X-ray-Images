from __future__ import division, print_function
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

import os
from PIL import Image
from pathlib import Path

import torch
import torchvision
from torchvision import transforms
torch.manual_seed(0)

app = Flask(__name__)

def model_predict(img_path):

    predict_transform = torchvision.transforms.Compose([
        torchvision.transforms.Resize(size=(224, 224)),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    model = torchvision.models.resnet18(pretrained=True)
    model.fc = torch.nn.Linear(in_features=512, out_features=3)
    checkpoint = torch.load(Path('resnet18-model.h5'))
    model.load_state_dict(checkpoint)

    model.eval()

    img=Image.open(img_path)
    if len(img.split()) == 3:
        return "Please provide valid image"
    image = Image.open(img_path).convert('RGB')
    image = predict_transform(image)
    print(image.shape)
    image = torch.unsqueeze(image, 0)
    print(image.shape)

    output = model(image)
    _, pred = torch.max(output, 1)
    pred=pred.item()

    label=""

    if pred==1:
        label="viral"
    elif pred==2:
        label = "covid"
    elif pred == 0:
        label = "normal"

    return label

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        return model_predict(file_path)

    return None


if __name__ == '__main__':
    app.run(debug=True)

