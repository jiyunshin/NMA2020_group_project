import ssm
from gelatolib import *
from sklearn.decomposition import PCA
from mpl_toolkits import mplot3d



# Analysis parameters
mouse = "Cori_2016-12-14"
area = 'MOs'
t1 = 0    # start time point (seconds)
t2 = 1600    # end time point (second)
dt = 0.02    # bin size (seconds)
N_PCs = 30   # number of principal components for PCA
N_states = 7   # number of states for HMM
plot_PCs = True    # True --> shows a 3D plot of first 3 PCs
allow_HMM = False    # True --> runs PCA and then HMM


# Collect and bin spikes
collect_mouse_data(mouse)
area_spikes = get_area(area)
binned_spikes = bin_spikes(area_spikes, t1, t2, dt)


# Perform PCA
X = binned_spikes.T
pca = PCA(n_components=N_PCs)
principalComponents = pca.fit_transform(X)
var_list = pca.explained_variance_ratio_
variance = np.sum(var_list)
print(f"\nVariance explained: {variance:.2f}")

if plot_PCs:
    # Create 3D plot of first 3 PCs
    ax = plt.axes(projection='3d')
    xline = principalComponents[:,0]
    yline = principalComponents[:,1]
    zline = principalComponents[:,2]
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_zlabel('PC3')
    ax.plot3D(xline, yline, zline, 'o', ms=0.5)
    plt.show()

if allow_HMM:
    # Create HMM model
    data = principalComponents
    model = ssm.HMM(N_states, N_PCs, observations="gaussian")
    hmm_lls = model.fit(data, method="em", num_iters=100)
    posteriors = model.filter(data)
    
    # Plot log likelihood to see if EM converged
    plt.figure()
    plt.plot(hmm_lls, label="EM")
    plt.xlabel("EM Iteration")
    plt.ylabel("Log Probability")
    plt.legend(loc="lower right")
    
    plt.figure(figsize=[9,5])
    for s in range(N_states):
        plt.plot(posteriors[:, s], label="State %d" % s)
    plt.suptitle('Posterior probability of latent states')
    plt.xlabel(f'time bin')
    plt.ylabel('probability')
    plt.legend()
    
    plt.show()
