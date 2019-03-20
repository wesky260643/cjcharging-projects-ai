#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File Name : cifar10_classifer_pytorch.py
# @Purpose :
# @Creation Date : 2019-03-20 11:37:23
# @Last Modified : 2019-03-20 15:47:08
# @Created By :  chenjiang
# @Modified By :  chenjiang


from os import sys, path
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as Function
import torch.optim as optim
# import matplotlib.pyplot as plt
import numpy as np

# ---- data load
transform = transforms.Compose(
        [transforms.ToTensor(), 
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


trainset = torchvision.datasets.CIFAR10(root="./data", train=True, 
        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=4, shuffle=True, 
        num_workers=2)

testset = torchvision.datasets.CIFAR10(root="./data", train=False, 
        download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4, shuffle=False,
        num_workers=2)

classes = ('plane', 'car', 'bird', 'cat',
        'deer', 'dog', 'frog', 'horse', 'ship', 'truck')


# functions to show an image
# def imshow(img):
#     img = img / 2 + 0.5     # unnormalize
#     npimg = img.numpy()
#     plt.imshow(np.transpose(npimg, (1, 2, 0)))
#     plt.show()


# get some random training images
dataiter = iter(trainloader)
images, labels = dataiter.next()

# show images
# imshow(torchvision.utils.make_grid(images))
# print labels
print(' '.join('%5s' % classes[labels[j]] for j in range(4)))


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16*5*5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(Function.relu(self.conv1(x)))
        x = self.pool(Function.relu(self.conv2(x)))
        x = x.view(-1, 16*5*5)
        x = Function.relu(self.fc1(x))
        x = Function.relu(self.fc2(x))
        x = self.fc3(x)
        return x

net = Net()


criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# ---------- train
for epoch in range(2):
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        inputs, labels = data

        optimizer.zero_grad()

        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        if i%2000 == 1999:
            print('[%d, %5d] loss: %.3f' % 
                    (epoch + 1, i + 1, running_loss / 2000))
            runing_loss = 0.0
print("finish training")


# ---------- test
dataiter = iter(testloader)
images, labels = dataiter.next()

# imshow(torchvision.utils.make_grid(images))
print("groundTruth: ", " ".join("%5s" % classes[labels[j]] 
    for j in range(4)))

outputs = net(images)

_, predicted = torch.max(outputs, 1)

print("predicted: ", " ".join("%5s" % classes[predicted[j]] 
    for j in range(4)))


# ---- how perform
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print("accuracy of the network on the 10000 test images: %d %%" % 
        (100*correct/total))


## perfor by classes
class_correct = list(0. for i in range(10))
class_total = list(0. for i in range(10))
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        c = (predicted == labels).squeeze()
        for i in range(4):
            label = labels[i]
            class_correct[label] += c[i].item()
            class_total[label] += 1

for i in range(10):
    print("accuracy of %5s : %2d %%" % 
            (classes[i], 100*class_correct[i]/class_total[i]))

