import_images.py

This script processes annotation data from LabelMe JSON files and outputs a structured CSV dataset for ML use.

1. Setup Paths and Variables
- `labelme_dir`: Path to folder with LabelMe `.json` files.
- `output_csv`: Output CSV file name.
- `records`: List to store parsed data.

2. Iterate Over JSON Files
- Loops through `.json` files in the specified directory.

3. Read and Parse JSON Content
- Loads each JSON file into a dictionary using `json.load()`.

4. Extract Image Metadata
- Gets the image file name and dimensions (`imageWidth`, `imageHeight`).

5. Extract and Parse Labels
- For each shape in the annotations, extract the label.
- Expected label format: `Shoe (x_offset, z_distance, angle)`.
  - `x_offset`: lateral position from screen center (mm).
  - `z_distance`: distance from camera (mm).
  - `angle`: viewing angle (degrees).

6. Normalize and Compute Features
- `x_offset_norm = x_offset / (width / 2)` (normalized -1 to 1 range).
- `z_distance_norm = z_distance / 2000.0` (for 2m max distance).
- Converts angle to radians and calculates:
  - `angle_sin = sin(angle)`
  - `angle_cos = cos(angle)`

7. Append to Records
- Each annotation is saved as a dictionary and appended to the list.

8. Save to CSV
- Converts `records` into a DataFrame and writes it to `output_csv`.

Final CSV Columns:
- image, x_offset, z_distance, angle
- x_offset_norm, z_distance_norm
- angle_sin, angle_cos
------------------------------------------------------------------------------------------------------------------------------------------

train.py

This script is for training a deep learning regression model to predict a shoe's position and orientation from images.
Here’s a breakdown:

1. IMPORTS:
   - Standard libraries (os, pandas, PIL) for file I/O and image processing.
   - PyTorch libraries for model definition, training, and dataset handling.
   - torchvision for transforms and pre-trained models.

2. SHOE DATASET CLASS:
   - Reads a CSV with annotations (e.g., x_offset_norm, z_distance_norm, angle_sin, angle_cos).
   - Loads images from the given directory.
   - Applies transformations if provided.
   - Returns image and corresponding target vector (4D regression target).

3. MODEL (ShoeRegressor):
   - Uses a pre-trained ResNet18 as the feature extractor.
   - Replaces its final layer to output 4 continuous values.

4. TRAIN FUNCTION:
   - Sets hyperparameters (batch size, epochs, learning rate, validation split, paths).
   - Defines two sets of transformations: training (with augmentations) and validation (basic).
   - Loads the full dataset and splits it into training and validation sets.
   - Sets appropriate transforms for each split.
   - Defines data loaders for batching.
   - Moves the model to GPU if available.
   - Defines Mean Squared Error (MSE) as the loss function.
   - Uses Adam optimizer for training.

5. TRAINING LOOP:
   - Loops over epochs, performing training and validation in each.
   - During training: computes loss, backpropagates, and updates weights.
   - During validation: evaluates model performance without updating weights.
   - Prints average training and validation loss per epoch.

6. SAVING:
   - Saves the trained model to "shoe_model.pth".

USAGE:
   - Run the script. It will read from the dataset, train the model, and save it for later use.
------------------------------------------------------------------------------------------------------------------------------------------
live_predict.py

This script runs a live inference pipeline using a trained ResNet-18 model on frames captured from an OAK-D camera using DepthAI. The model predicts the shoe’s x-offset from screen center, its distance from the camera, and its angle.

---

### 1. **Model Setup**
```python
torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 4)
```
- Sets device to GPU if available.
- Uses ResNet-18 with the final layer modified for 4 regression outputs.

```python
state_dict = torch.load("shoe_model.pth")
cleaned_state_dict = {k.replace("backbone.", ""): v for k, v in state_dict.items()}
model.load_state_dict(cleaned_state_dict)
```
- Loads trained weights, removing any "backbone." prefix.

---

### 2. **Image Transformations**
```python
transform = transforms.Compose([...])
```
- Applies resizing, tensor conversion, and normalization to match training conditions.

---

### 3. **DepthAI Pipeline Setup**
```python
pipeline = dai.Pipeline()
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
```
- Initializes the RGB camera (CAM_A) and sets frame size to 640x480.

```python
xout_video = pipeline.createXLinkOut()
cam_rgb.preview.link(xout_video.input)
```
- Connects the camera to an output stream for real-time display.

---

### 4. **Inference Loop**
```python
with dai.Device(pipeline) as depthai_device:
    video = depthai_device.getOutputQueue(name="video")
```
- Starts the camera pipeline and fetches frames continuously.

```python
input_tensor = transform(frame).unsqueeze(0).to(torch_device)
prediction = model(input_tensor).squeeze().cpu().numpy()
```
- Converts the frame to a tensor and passes it to the model for prediction.

---

### 5. **Prediction Parsing**
```python
x_offset_norm, z_distance_norm, sin_theta, cos_theta = prediction
x_offset = x_offset_norm * frame_width
z_distance = z_distance_norm * 2000
angle_deg = np.degrees(np.arctan2(sin_theta, cos_theta)) % 360
```
- Converts normalized predictions into actual values for display.

---

### 6. **Display Output**
```python
cv2.putText(...)
cv2.imshow("Shoe Tracker", frame)
```
- Draws the x-offset, distance, and angle predictions on the frame.
- Press `q` to quit.

---

### 7. **Cleanup**
```python
cv2.destroyAllWindows()
```
- Closes all OpenCV windows after the loop ends.
-----------------------------------------------------------------------------------------------------------------------------------------