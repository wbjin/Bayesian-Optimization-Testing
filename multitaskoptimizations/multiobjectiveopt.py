import gpytorch
import torch

import numpy as np

import pandas as pd

from scipy.stats import norm

import time
class MultitaskGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood, params, numTasks):
        super(MultitaskGPModel, self).__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.MultitaskMean(
            gpytorch.means.ConstantMean(), num_tasks=numTasks
        )
        self.covar_module = gpytorch.kernels.MultitaskKernel(
            gpytorch.kernels.RBFKernel(), num_tasks=numTasks, rank=1
        )

    def forward(self, x):
        mean_x = self.mean_module(x)
        covar_x = self.covar_module(x)
        return gpytorch.distributions.MultitaskMultivariateNormal(mean_x, covar_x)
    
class Optimizer:
    def __init__(self, X, y):
        self.X = X
        self.y = y
        self.numInput = self.X.size(0)
        self.numTasks = len(self.y[0])
        self.params = len(self.X[0])
        time.sleep(3)
        self.domain = [[7, 9], [0, 1], [0, 1.31]]
        self.range1 = self.domain[0][1]-self.domain[0][0]
        self.range2 = self.domain[1][1]-self.domain[1][0]
        self.range3 = self.domain[2][1]-self.domain[2][0]
    
    def run(self):
        self.trainGP()
        for i in range(10):
            self.modelSurrogate()
            self.evaluateNext()
        self.modelSurrogate()
        
    def trainGP(self, trainIter = 10):
        self.likelihood = gpytorch.likelihoods.MultitaskGaussianLikelihood(num_tasks=self.numTasks)
        self.model = MultitaskGPModel(self.X, self.y, self.likelihood, self.params, self.numTasks)

        self.model.train()
        self.likelihood.train()

        mll = gpytorch.mlls.ExactMarginalLogLikelihood(self.likelihood, self.model)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.1)

        for i in range(20):
            optimizer.zero_grad()
            output = self.model(self.X)
            loss = -mll(output, self.y)
            loss.backward()
            optimizer.step()

        self.model.eval()
        self.observedPred = (self.model(self.X))
    
    def modelSurrogate(self, *args):
        self.prediction = self.likelihood(self.model(self.X)).mean.detach().numpy()
        if args:
            return self.likelihood(self.model(args[0])).mean.detach().numpy()


    def acquisitionFunction(self):
        explorationWidth = 20
        exploreX1 = self.range1*torch.rand(int(explorationWidth))+self.domain[0][0]
        exploreX2 = self.range2*torch.rand(int(explorationWidth))+self.domain[1][0]
        explorationPoints = []
        for i in range(21):
            explorationPoints.append(self.range3*torch.rand(int(explorationWidth))+self.domain[2][0])
        exploreX = torch.stack([exploreX1, exploreX2, explorationPoints[0], explorationPoints[1], explorationPoints[2],
                                explorationPoints[3], explorationPoints[4], explorationPoints[5], explorationPoints[6], 
                                explorationPoints[7], explorationPoints[8], explorationPoints[9], explorationPoints[10], 
                                explorationPoints[11], explorationPoints[12], explorationPoints[13], explorationPoints[14],
                                explorationPoints[15], explorationPoints[16], explorationPoints[17], explorationPoints[18],
                                explorationPoints[19], explorationPoints[20]], -1)
        bestScore = self.prediction[0][1]+self.prediction[0][2]+self.prediction[0][3]-self.prediction[0][0]
        for i in range(len(self.prediction)):
            score = self.prediction[i][1]+self.prediction[i][2]+self.prediction[i][3]-self.prediction[i][0]
            if score > bestScore:
                bestScore = score
        observedPred = (self.model(exploreX))
        exploreY = self.likelihood(observedPred).mean.detach().numpy()
        scoredY = []
        for item in exploreY:
            scoredY.append(item[1]+item[2]+item[3]-item[0])
        scoredY = np.array(scoredY)
        stdev = np.sqrt(scoredY)
        z = (scoredY - bestScore)/stdev
        cdf = norm.cdf(z)
        index = np.argmax(cdf)
        newX = exploreX[index]
        return newX, index
    def evaluateNext(self):
        newX, index = self.acquisitionFunction()
        self.X = torch.cat((self.X, newX.unsqueeze(0)), 0)
    def result(self):
        bestIndex = 0
        bestScore = self.prediction[0][1]+self.prediction[0][2]+self.prediction[0][3]-self.prediction[0][0]
        for i in range(len(self.prediction)):
            score = self.prediction[i][1]+self.prediction[i][2]+self.prediction[i][3]-self.prediction[i][0]
            if score > bestScore:
                bestScore = score
                bestIndex = i
        
        return score, self.X[bestIndex], self.prediction[bestIndex]

        
def main():
    filename = 'testdata/multiparam.xlsx'
    df = pd.read_excel(filename)
    df = df.drop(index = 0)
    A = torch.tensor(df["A"].to_numpy()[:23])
    B = torch.tensor(df["B"].to_numpy()[:23])
    C = torch.tensor(df["C"].to_numpy()[:23])
    D = torch.tensor(df["d"].to_numpy()[:23])
    E = torch.tensor(df["E"].to_numpy()[:23])
    F = torch.tensor(df["F"].to_numpy()[:23])
    G = torch.tensor(df["G"].to_numpy()[:23])
    H = torch.tensor(df["H"].to_numpy()[:23])
    I = torch.tensor(df["I"].to_numpy()[:23])
    J = torch.tensor(df["J"].to_numpy()[:23])
    K = torch.tensor(df["K"].to_numpy()[:23])
    L = torch.tensor(df["L"].to_numpy()[:23])
    M = torch.tensor(df["M"].to_numpy()[:23])
    N = torch.tensor(df["N"].to_numpy()[:23].astype('float64'))
    O = torch.tensor(df["O"].to_numpy()[:23])
    P = torch.tensor(df["P"].to_numpy()[:23])
    Q = torch.tensor(df["Q"].to_numpy()[:23])
    R = torch.tensor(df["R"].to_numpy()[:23])
    S = torch.tensor(df["S"].to_numpy()[:23])
    T = torch.tensor(df["T"].to_numpy()[:23])
    U = torch.tensor(df["U"].to_numpy()[:23])
    V = torch.tensor(df["V"].to_numpy()[:23])
    W = torch.tensor(df["W"].to_numpy()[:23])

    X = torch.stack([A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W], -1).float()
    y1 = torch.from_numpy(df["DT"].to_numpy()[:23].astype('float64'))
    y2 = torch.from_numpy(df["r"].to_numpy()[:23].astype('float64'))
    y3 = torch.from_numpy(df["R0"].to_numpy()[:23].astype('float64'))
    y4 = torch.from_numpy(df["TL"].to_numpy()[:23].astype('float64'))
    y = torch.stack([y1, y2, y3, y4], -1).float()
    #some experiemnts with 3 params, some with more, optimize each experiment and find the best output
    #optimize with all the params 
    params = ["C", "d", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W"]
    optimizer = Optimizer(X, y)
    optimizer.run()
    # optimizer.trainGP()
    # optimizer.modelSurrogate()
    _, params, output = optimizer.result()
    print("Optimization results: -------------------------------")
    print("Params A to W")
    for i in range(len(params)):
        param = chr(ord("A") + i)
        print(param, ": ", round(params[i].item(), 3))
    print("Output: ")
    print("DT: ", output[0])
    print("r: ", output[1])
    print("R0: ", output[2])
    print("TL: ", output[3])

def run_bayesian_optimization():
    filename = 'testdata/multiparam.xlsx'
    df = pd.read_excel(filename)
    df = df.drop(index = 0)
    A = torch.tensor(df["A"].to_numpy()[:23])
    B = torch.tensor(df["B"].to_numpy()[:23])
    C = torch.tensor(df["C"].to_numpy()[:23])
    D = torch.tensor(df["d"].to_numpy()[:23])
    E = torch.tensor(df["E"].to_numpy()[:23])
    F = torch.tensor(df["F"].to_numpy()[:23])
    G = torch.tensor(df["G"].to_numpy()[:23])
    H = torch.tensor(df["H"].to_numpy()[:23])
    I = torch.tensor(df["I"].to_numpy()[:23])
    J = torch.tensor(df["J"].to_numpy()[:23])
    K = torch.tensor(df["K"].to_numpy()[:23])
    L = torch.tensor(df["L"].to_numpy()[:23])
    M = torch.tensor(df["M"].to_numpy()[:23])
    N = torch.tensor(df["N"].to_numpy()[:23].astype('float64'))
    O = torch.tensor(df["O"].to_numpy()[:23])
    P = torch.tensor(df["P"].to_numpy()[:23])
    Q = torch.tensor(df["Q"].to_numpy()[:23])
    R = torch.tensor(df["R"].to_numpy()[:23])
    S = torch.tensor(df["S"].to_numpy()[:23])
    T = torch.tensor(df["T"].to_numpy()[:23])
    U = torch.tensor(df["U"].to_numpy()[:23])
    V = torch.tensor(df["V"].to_numpy()[:23])
    W = torch.tensor(df["W"].to_numpy()[:23])

    X = torch.stack([A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W], -1).float()
    y1 = torch.from_numpy(df["DT"].to_numpy()[:23].astype('float64'))
    y2 = torch.from_numpy(df["r"].to_numpy()[:23].astype('float64'))
    y3 = torch.from_numpy(df["R0"].to_numpy()[:23].astype('float64'))
    y4 = torch.from_numpy(df["TL"].to_numpy()[:23].astype('float64'))
    y = torch.stack([y1, y2, y3, y4], -1).float()
    #some experiemnts with 3 params, some with more, optimize each experiment and find the best output
    #optimize with all the params 
    params = ["C", "d", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W"]
    optimizer = Optimizer(X, y)
    optimizer.run()
    _, params, output = optimizer.result()
    output[output<0]*=-1
    return params, output
