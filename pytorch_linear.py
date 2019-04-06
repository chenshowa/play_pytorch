import torch
import matplotlib.pyplot as plt

x = torch.unsqueeze(torch.linspace(-1, 1, 100), dim=1)  # x data (tensor), shape=(100, 1)
# unsqueeze() : transform 1 dimension to 2 dimensions
# 一定要轉為2維才能執行做運算
y = x.pow(2) + 0.2*torch.rand(x.size())                 # noisy y data (tensor), shape=(100, 1)

# plot scatter
plt.scatter(x.data.numpy(), y.data.numpy())
plt.show()



import torch
import torch.nn.functional as F     # 激勵涵數

class Net(torch.nn.Module):  # 繼承 torch 的 Module
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()     # 繼承 __init__ 功能
        # pytorch搭建net的起手式

        # 定義每層用什樣的形式
        self.hidden = torch.nn.Linear(n_feature, n_hidden)   # 隱藏層線性輸出 #hidden是自命名
        self.predict = torch.nn.Linear(n_hidden, n_output)   # 輸出層線性輸出 #承接hidden的神經

    def forward(self, x):   # 這同時也是 Module 中的 forward 功能 # x是輸入data
        # 正向傳播輸入值, 神经网络分析出输出值
        x = F.relu(self.hidden(x))      # 激勵函数(隱藏層的線性值) #data 先經過hidden 再經由relu激活
        x = self.predict(x)             # 輸出值 #%注意 這裡不用激勵函數 壓縮輸出值
        return x

net = Net(n_feature=1, n_hidden=10, n_output=1)

print(net)  # net 的结构
"""
Net (
  (hidden): Linear (1 -> 10)
  (predict): Linear (10 -> 1)
)
"""



# optimizer 是訓練神經網絡參數的工具
optimizer = torch.optim.SGD(net.parameters(), lr=0.2)  # 傳入 net 的所有参数, 学习率
# net.parameters() 是用來傳入神經網絡的參數
loss_func = torch.nn.MSELoss()      # 預測值和實際值的誤差计算公式 (均方差)

for t in range(100):
    prediction = net(x)     # 餵给 net 訓練數據 x, 輸出預測值 

    loss = loss_func(prediction, y)     # 計算兩者的誤差 # 預測值在前和實際值後

    optimizer.zero_grad()   # 清空上一步的殘餘更新參数值 將梯度降為0
    loss.backward()         # 誤差反向傳遞, 計算参数更新值
    optimizer.step()        # 將參数更新值更新到 net 的 parameters 上

    print(loss.data.numpy())# 輸出誤差值