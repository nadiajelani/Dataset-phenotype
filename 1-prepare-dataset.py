from datasets import load_dataset, get_dataset_config_names
import pickle
import cv2
import os

print(get_dataset_config_names("tonyFang04/8-calves"))

video_ds = load_dataset("tonyFang04/8-calves", "videos")
sample = video_ds["train"][0]

with open("calf_video.mp4", "wb") as f:
    f.write(sample["mp4"])

with open("calf_data.pkl", "wb") as f:
    f.write(sample["pkl"])

with open("calf_data.pkl", "rb") as f:
    data = pickle.load(f)

print(type(data))
print(data.head())
print("Unique calves:", data["tracklet_id"].nunique())
print(data["tracklet_id"].value_counts())

os.makedirs("frames", exist_ok=True)

cap = cv2.VideoCapture("calf_video.mp4")
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imwrite(f"frames/frame_{frame_count:05d}.jpg", frame)
    frame_count += 1

cap.release()

print(f"Extracted {frame_count} frames")
print("Saved calf_video.mp4, calf_data.pkl, and frames folder")