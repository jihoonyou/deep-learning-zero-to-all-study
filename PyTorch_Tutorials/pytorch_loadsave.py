# Imports
import torch
import torch.nn as nn # all network module
import torch.optim as optim # all the optimizer algorithms
import torch.nn.functional as F # all the fuctions w/o parameters ex) LeRu
from torch.utils.data import DataLoader # easier data management
import torchvision.datasets as datasets # pytorch standard dataset
import torchvision.transforms as transforms # 

# Create Fully Conneceted Network
class NN(nn.Module):
    def __init__(self, input_size, num_classes): # MINST dataset 28x28 = 784
        super(NN, self).__init__() # call parent's init
        self.fc1 = nn.Linear(input_size, 50)
        self.fc2 = nn.Linear(50, num_classes)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class CNN(nn.Module):
    def __init__(self, in_channels = 1, num_classes = 10):
        super(CNN, self).__init__() # call parent's init
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=8, kernel_size=(3,3), stride=(1,1), padding=(1,1)) # keep the same dimension
        self.pool = nn.MaxPool2d(kernel_size=(2,2), stride = (2,2))
        self.conv2 = nn.Conv2d(in_channels=8, out_channels=16, kernel_size=(3,3), stride=(1,1), padding=(1,1))
        self.fc1 = nn.Linear(16*7*7, num_classes)
    
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc1(x)

        return x

def save_checkpoint(state, filename='my_checkpoint.pth.tar'):
    print('=> Saving checkpoint')
    torch.save(state, filename)

def load_checkpoint(checkpoint):
    print('=> Loading checkpoint')
    model.load_state_dict(checkpoint['state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer'])

if load_model:
    load_model(torch.load('my_checkpoint.pth.tar'))

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Hyperparameters
in_channel = 1
num_classes = 10
learning_rate = 0.001
batch_size = 64 # 한번에 학습시킬 data들 묶음
num_epochs = 5
load_model = True

# Load Data
train_dataset = datasets.MNIST(root='dataset/', train = True, transform=transforms.ToTensor(), download=True) # download data
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_dataset = datasets.MNIST(root='dataset/', train = False, transform=transforms.ToTensor(), download=True) # download data
test_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)


# Initialize network
model = CNN().to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate) # 모델의 parameters 

# Train Netowrk
for epoch in range(num_epochs):
    
    if epoch % 3 == 0:
        checkpoint = { 'state_dict': model.state_dict(), 'optimzer': optimzer.state_dict()}
        save_checkpoint(checkpoint)
    for batch, (data, targets) in enumerate(train_loader): # data is images, targets are correct digits for each image
        data = data.to(device=device)
        targets = targets.to(device=device)
        # print(data.shape) # [64, 1, 28, 28] => [Num_of_images, black_or_white, size_of_images]
        
        # forward
        scores = model(data)
        loss = criterion(scores, targets)

        # backward
        optimizer.zero_grad()
        loss.backward()

        # gradient descent or adam step
        optimizer.step()

# Check accruacy on training & test to see hwo good our model
def check_accuracy(loader, model):
    if loader.dataset.train:
        print('Checking accuracy on training data')
    else:
        print('Checking accuracy on test data')
    num_correct = 0
    num_samples = 0
    model.eval() 

    with torch.no_grad(): #unnecessary computation / no gradient calculation
        for x, y in loader:
            x = x.to(device=device)
            y = y.to(device=device)

            scores = model(x) # 64x10
            _, predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)
        print(f'Got {num_correct} / {num_samples} with accuracy {float(num_correct)/float(num_samples)*100:.2f}')

    model.train()

check_accuracy(train_loader, model)
check_accuracy(test_loader, model)