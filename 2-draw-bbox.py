from datasets import load_dataset

dataset = load_dataset("tonyFang04/8-calves", "images")
sample = dataset["train"][0]

for key, value in sample.items():
    print("\n---", key, "---")
    print("TYPE:", type(value))
    print("VALUE:", repr(value)[:500])
img = sample["png"]
print(type(img))
print(img.size)
img.save("sample_8calves.png")
print("Saved sample_8calves.png")
print(dataset["train"].features)