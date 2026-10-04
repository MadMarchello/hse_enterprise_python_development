import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image

if torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

image_path = Path("photos/Beagle_1.jpg")
checkpoint_path = Path("dog_breeds_v2.pth")

print("device:", device)
print("фото:", image_path.resolve())
print("чекпоинт:", checkpoint_path.resolve())


weights = ResNet18_Weights.DEFAULT
transform = weights.transforms()


train_all = datasets.OxfordIIITPet(
    root="./data",
    split="trainval",
    target_types="category",
    download=True,
)
test_all = datasets.OxfordIIITPet(
    root="./data",
    split="test",
    target_types="category",
    download=True,
)

print(len(train_all), len(test_all))
print(train_all.classes)

breeds = [
    "American Bulldog",
    "American Pit Bull Terrier",
    "Basset Hound",
    "Beagle",
    "Boxer",
    "Chihuahua",
    "English Cocker Spaniel",
    "English Setter",
    "German Shorthaired",
    "Great Pyrenees",
    "Havanese",
    "Japanese Chin",
    "Keeshond",
    "Leonberger",
    "Miniature Pinscher",
    "Newfoundland",
    "Pomeranian",
    "Pug",
    "Saint Bernard",
    "Samoyed",
    "Scottish Terrier",
    "Shiba Inu",
    "Staffordshire Bull Terrier",
    "Wheaten Terrier",
    "Yorkshire Terrier",
]
other_name = "другие"
classes = breeds + [other_name]
other_id = len(breeds)

name_to_old = {
    name: i
    for i, name in enumerate(train_all.classes)
}
selected_old = [
    name_to_old[name]
    for name in breeds
]
old_to_new = {
    old: new
    for new, old in enumerate(selected_old)
}
print(old_to_new)
print("другие:", other_id)


def to_new_label(old_y):
    return old_to_new.get(old_y, other_id)


class BreedsWithOther(Dataset):
    def __init__(self, base, transform):
        self.base = base
        self.transform = transform

    def __len__(self):
        return len(self.base)

    def __getitem__(self, i):
        image, old_y = self.base[i]
        image = self.transform(image)
        return image, to_new_label(old_y)



label_counts = [0] * len(classes)
for old_y in train_all._labels:
    label_counts[to_new_label(old_y)] += 1

total_labels = sum(label_counts)
class_weights = torch.tensor(
    [
        total_labels / (len(classes) * count)
        for count in label_counts
    ],
    dtype=torch.float32,
)

print("примеров по классам:")
for name, count, weight in zip(classes, label_counts, class_weights.tolist()):
    print(f"{name:<28} {count:<5} вес {weight:.3f}")

train_ds = BreedsWithOther(train_all, transform)
test_ds = BreedsWithOther(test_all, transform)

train_loader = DataLoader(
    train_ds,
    batch_size=32,
    shuffle=True,
)
test_loader = DataLoader(
    test_ds,
    batch_size=32,
    shuffle=False,
)

X, y = next(iter(train_loader))
print(X.shape)
print(y.shape)
print("train", len(train_ds), "test", len(test_ds))


model = resnet18(weights=weights)

for p in model.parameters():
    p.requires_grad = False

model.fc = nn.Linear(
    model.fc.in_features,
    len(classes),
)
model = model.to(device)

criterion = nn.CrossEntropyLoss(
    weight=class_weights.to(device),
)
optimizer = torch.optim.SGD(
    model.fc.parameters(),
    lr=0.01,
    momentum=0.9,
)


epoch_losses = []
for epoch in range(5):
    model.train()
    for X, y in train_loader:
        X = X.to(device)
        y = y.to(device)

        optimizer.zero_grad()
        logits = model(X)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

    epoch_losses.append(loss.item())
    print(
        f"epoch={epoch + 1} "
        f"loss={loss.item():.4f}"
    )


model.eval()
correct = 0
total = 0
correct_by_class = [0] * len(classes)
total_by_class = [0] * len(classes)

with torch.no_grad():
    for X, y in test_loader:
        X = X.to(device)
        y = y.to(device)

        logits = model(X)
        pred = logits.argmax(dim=1)
        match = pred == y

        correct += match.sum().item()
        total += y.size(0)

        for class_id in range(len(classes)):
            mask = y == class_id
            total_by_class[class_id] += mask.sum().item()
            correct_by_class[class_id] += (match & mask).sum().item()

accuracy = correct / total
print(f"accuracy = {accuracy:.2%}")
print()
for name, ok, n in zip(classes, correct_by_class, total_by_class):
    print(f"{name:<28} {ok / n:.2%}  ({ok}/{n})")


torch.save(
    {
        "model_state": model.state_dict(),
        "classes": classes,
        "epoch_losses": epoch_losses,
    },
    checkpoint_path,
)
print("сохранено:", checkpoint_path.resolve())


try:
    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )
except TypeError:
    checkpoint = torch.load(checkpoint_path, map_location=device)

classes = checkpoint["classes"]
epoch_losses = checkpoint["epoch_losses"]

model = resnet18(weights=None)
model.fc = nn.Linear(
    model.fc.in_features,
    len(classes),
)
model.load_state_dict(checkpoint["model_state"])
model = model.to(device)
model.eval()

correct = 0
total = 0
correct_by_class = [0] * len(classes)
total_by_class = [0] * len(classes)
confusion = torch.zeros(len(classes), len(classes), dtype=torch.int64)

with torch.no_grad():
    for X, y in test_loader:
        X = X.to(device)
        y = y.to(device)
        pred = model(X).argmax(dim=1)
        match = pred == y

        correct += match.sum().item()
        total += y.size(0)

        for class_id in range(len(classes)):
            mask = y == class_id
            total_by_class[class_id] += int(mask.sum().item())
            correct_by_class[class_id] += int((match & mask).sum().item())

        for true_id, pred_id in zip(y.tolist(), pred.tolist()):
            confusion[true_id, pred_id] += 1

accuracy = correct / total
print("loss последнего батча по эпохам:")
for epoch, value in enumerate(epoch_losses, start=1):
    print(f"epoch={epoch} loss={value:.4f}")
print()
print(f"accuracy = {accuracy:.2%}")
print()
for name, ok, n in zip(classes, correct_by_class, total_by_class):
    print(f"{name:<28} {ok / n:.2%}  ({ok}/{n})")


Path("output").mkdir(exist_ok=True)

import matplotlib.pyplot as plt

plt.rcParams["font.size"] = 11

fig, ax = plt.subplots(figsize=(7, 4))
epochs = list(range(1, len(epoch_losses) + 1))
ax.plot(epochs, epoch_losses, marker="o", color="#3d6f8a")
ax.set_xticks(epochs)
ax.set_xlabel("Эпоха")
ax.set_ylabel("Loss последнего батча")
ax.set_title("Обучение: loss последнего батча эпохи")
fig.tight_layout()
fig.savefig("output/learning_loss.png")

accuracies = [
    ok / n
    for ok, n in zip(correct_by_class, total_by_class)
]
order = sorted(range(len(classes)), key=lambda i: accuracies[i])
names = [classes[i] for i in order]
values = [accuracies[i] * 100 for i in order]
colors = ["#b85c38" if value < 90 else "#3d6f8a" for value in values]

fig, ax = plt.subplots(figsize=(9, 10))
ax.barh(names, values, color=colors)
ax.axvline(
    accuracy * 100,
    color="#222222",
    linestyle="--",
    linewidth=1,
    label=f"общая {accuracy:.2%}",
)
ax.set_xlim(0, 100)
ax.set_xlabel("Accuracy, %")
ax.set_title("Accuracy по классам на test")
ax.legend(loc="lower right")
ax.invert_yaxis()
fig.tight_layout()
fig.savefig("output/accuracy_by_class.png")

share = confusion.float()
share = share / share.sum(dim=1, keepdim=True).clamp(min=1)
data = share.numpy()

fig, ax = plt.subplots(figsize=(14, 12))
image = ax.imshow(data, vmin=0, vmax=1, cmap="Blues")
ax.set_xticks(range(len(classes)), classes, rotation=90, fontsize=8)
ax.set_yticks(range(len(classes)), classes, fontsize=8)
ax.set_xlabel("Предсказание")
ax.set_ylabel("Истинный класс")
ax.set_title("Доля предсказаний внутри истинного класса")
for i in range(len(classes)):
    for j in range(len(classes)):
        value = float(data[i, j])
        if value < 0.04:
            continue
        ax.text(
            j,
            i,
            f"{value:.0%}",
            ha="center",
            va="center",
            fontsize=6,
            color="white" if value > 0.55 else "#1a1a1a",
        )
fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
fig.tight_layout()
fig.savefig("output/confusion_matrix.png")


if not checkpoint_path.is_file():
    raise FileNotFoundError(
        f"Нет {checkpoint_path.resolve()}. Сначала выполните ячейки обучения и сохранения."
    )

weights = ResNet18_Weights.DEFAULT
transform = weights.transforms()

try:
    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )
except TypeError:
    checkpoint = torch.load(checkpoint_path, map_location=device)

classes = checkpoint["classes"]

model = resnet18(weights=None)
model.fc = nn.Linear(
    model.fc.in_features,
    len(classes),
)
model.load_state_dict(checkpoint["model_state"])
model = model.to(device)
model.eval()


def predict(image):
    x = transform(image)
    x = x.unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)
        probabilities = torch.softmax(logits, dim=1)
    class_id = probabilities.argmax(dim=1).item()
    return class_id, probabilities[0]


def show_probabilities(class_id, probabilities):
    print(classes[class_id], f"{probabilities[class_id].item():.1%}")
    print()
    for name, probability in zip(classes, probabilities.tolist()):
        print(f"{name:<28} {probability:.1%}")


print("классы:", classes)


other_index = next(
    i
    for i, old_y in enumerate(test_all._labels)
    if old_y not in old_to_new
)
other_image, old_y = test_all[other_index]

other_image.save("output/other_dataset.png")
print("в датасете:", test_all.classes[old_y])

class_id, probabilities = predict(other_image)
show_probabilities(class_id, probabilities)


photo_candidates = [
    image_path,
    Path("photos/Beagle_1.jpg"),
    Path("dog.jpg"),
]
photo_path = next(
    (path for path in photo_candidates if path.is_file()),
    None,
)
if photo_path is None:
    raise FileNotFoundError(
        "Нет снимка для распознавания. "
        f"Проверены: {', '.join(str(path.resolve()) for path in photo_candidates)}."
    )
image_path = photo_path
print("фото:", image_path.resolve())

image = Image.open(image_path).convert("RGB")
x = transform(image)
print(x.shape)

x = x.unsqueeze(0)
print(x.shape)

image.save("output/photo.png")
class_id, probabilities = predict(image)
show_probabilities(class_id, probabilities)


car_path = Path("photos/car.jpg")
if not car_path.is_file():
    raise FileNotFoundError(
        f"Нет фото {car_path.resolve()}."
    )

car = Image.open(car_path).convert("RGB")
print("фото:", car_path.resolve())
car.save("output/car.png")

class_id, probabilities = predict(car)
show_probabilities(class_id, probabilities)


katya_dog_pth = Path("/Users/madmarchello/2026-10-01T16_32_33.314.jpeg")
if not katya_dog_pth.is_file():
    raise FileNotFoundError(
        f"Нет фото {katya_dog_pth.resolve()}."
    )

car = Image.open(katya_dog_pth).convert("RGB")
print("фото:", katya_dog_pth.resolve())
car.save("output/katya_dog.png")

class_id, probabilities = predict(car)
show_probabilities(class_id, probabilities)
