import argparse
import os
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter


def plot_time(x, ys, title, xlabel, ylabels, save_path=None):
    """
    Plot multiple lines with different y-axes on separate axes within the same figure.

    Parameters:
        x (array-like): The x-axis data.
        ys (list of array-like): List of y-axis data arrays.
        titles (list of str): List of titles for the plots.
        xlabel (str): The label for the x-axis.
        ylabels (list of str): List of labels for the y-axes.
        save_path (str, optional): Path to save the plot image. If None, the plot is displayed.
    """
    fig, ax1 = plt.subplots()

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabels[0], color='tab:blue')
    ax1.plot(x, ys[0], color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel(ylabels[1], color='tab:red')
    ax2.plot(x, ys[1], linestyle='dashed', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    ax3 = ax1.twinx()
    # Offset the second and third y-axes
    offset = 30
    ax3.spines['right'].set_position(('outward', 2 * offset))

    ax3.set_ylabel(ylabels[2], color='tab:orange')
    ax3.plot(x, ys[2], linestyle='dotted', color='tab:orange')
    ax3.tick_params(axis='y', labelcolor='tab:orange')

    # Set y-axis formatter to scientific notation (1e6)
    for ax in [ax1, ax2, ax3]:
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    fig.tight_layout()
    plt.title(title)  # Set title for the entire figure

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

def hist_time(categories, values, xlabel, ylabel, save_path=None):
    # Set the width of the bars
    bar_width = 0.35

    # Set the positions of the bars on the x-axis
    r1 = np.arange(len(categories))

    # Plot the bars
    plt.figure(figsize=(10, 6))  # Set the figure size
    bars = plt.bar(r1, values, color='b', width=bar_width, edgecolor='grey')

    # Add text labels above each bar
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, '%d' % int(value), ha='center', va='bottom')

    # Add xticks on the middle of the bars
    plt.xlabel(xlabel, fontweight='bold')
    plt.ylabel(ylabel, fontweight='bold')
    plt.xticks([r for r in range(len(categories))], categories)


    # Add legend
    # plt.legend()

    # Show plot
    plt.title('Pipelined Instruction Start-up Optimization')

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vector Core Time Simulator')
    parser.add_argument('--odir', default="./figures", type=str, help='Path to save outputs.')
    args = parser.parse_args()

    odir = os.path.abspath(args.odir)
    # Create the output directory if it does not exist
    os.makedirs(odir, exist_ok=True)
    print("Saving outputs to:", odir)

    ylables = ["Dot Product", "Fully Connected", "Convolution"]
    ylables = [label + " - Time (cycles)" for label in ylables]

    # plot for number of lanes
    numLanes = [2 ** (i + 2) for i in range(6)]
    numLanes = [math.log2(lane) for lane in numLanes]
    dot_product_time = [2060, 1981, 1942, 1923, 1914, 1914]
    fully_connected_time = [156058, 147866, 143770, 141722, 140698, 140698]
    convolution_time = [237248, 227088, 222389, 220103, 218960, 218960]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "lanes.png")
    plot_time(numLanes, ys, "", "Number of Lanes (log2)", ylables, save_path)

    # plot for number of banks
    vdmNumBanks = [ i + 1 for i in range(6)]
    dot_product_time = [3304, 2060, 2060, 2060, 2060, 2060]
    fully_connected_time = [237454, 156058, 139930, 156058, 139930, 139930]
    convolution_time = [397268, 381266, 237248, 237248, 237248, 237248]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "banks.png")
    plot_time(vdmNumBanks, ys, "", "Number of Banks", ylables, save_path)

    # plot for bank busy time
    vdmBankBusyTime = [ 2 ** i for i in range(6)]
    vdmBankBusyTime = [math.log2(time) for time in vdmBankBusyTime]
    dot_product_time = [2060, 2134, 2282, 2578, 4034, 6946]
    fully_connected_time = [156058, 191410, 262114, 403522, 748154, 1438018]
    convolution_time = [237248, 242328, 252488, 400824, 709688, 1327416]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "bank_busy_time.png")
    plot_time(vdmBankBusyTime, ys, "", "Bank Busy Time (log2)", ylables, save_path)

    # plot for data queue depth
    dataQueueDepth = [ i + 1 for i in range(6)]
    dot_product_time = [2060, 2060, 2060, 2060, 2060, 2060]
    fully_connected_time = [156058, 156058, 156058, 156058, 156058, 156058]
    convolution_time = [237248, 237248, 237248, 237248, 237248, 237248]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "data_queue_depth.png")
    plot_time(dataQueueDepth, ys, "", "Data Queue Depth", ylables, save_path)

    # plot for compute queue depth
    computeQueueDepth = [ i + 1 for i in range(6)]
    dot_product_time = [2060, 2060, 2060, 2060, 2060, 2060]
    fully_connected_time = [156058, 156058, 156058, 156058, 156058, 156058]
    convolution_time = [238264, 237248, 237248, 237248, 237248, 237248]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "compute_queue_depth.png")
    plot_time(computeQueueDepth, ys, "", "Compute Queue Depth", ylables, save_path)

    # plot for pipeline depth for vector load-save unit
    vlsPipelineDepth = [ i + 8 for i in range(6)]
    dot_product_time = [1949, 1986, 2023, 2060, 2097, 2134]
    fully_connected_time = [151414, 152962, 154510, 156058, 157606, 159154]
    convolution_time = [229628, 232168, 234708, 237248, 239788, 242328]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "vls_pipeline_depth.png")
    plot_time(vlsPipelineDepth, ys, "", "VLS Pipeline Depth", ylables, save_path)

    # plot for pipeline depth for vector multiply
    pipelineDepthMul = [ i + 9 for i in range(6)]
    dot_product_time = [2033, 2042, 2051, 2060, 2069, 2078]
    fully_connected_time = [155290, 155546, 155802, 156058, 156314, 156570]
    convolution_time = [233819, 234962, 236105, 237248, 238391, 239534]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "pipeline_depth_mul.png")
    plot_time(pipelineDepthMul, ys, "", "Multiply Pipeline Depth", ylables, save_path)

    # plot for pipeline depth for vector add
    pipelineDepthAdd = [ i + 1 for i in range(6)]
    dot_product_time = [2053, 2060, 2067, 2074, 2081, 2088]
    fully_connected_time = [155290, 156058, 156826, 157594, 158362, 159130]
    convolution_time = [237121, 237248, 237375, 237502, 237629, 237756]
    ys = [dot_product_time, fully_connected_time, convolution_time]
    save_path = os.path.join(args.odir, "pipeline_depth_add.png")
    plot_time(pipelineDepthAdd, ys, "", "Add Pipeline Depth", ylables, save_path)

    # # plot for optimazation: pipelined start-up
    # functions = ["No optimization", "Pipelined start-up"]
    # dot_product_time = [2060, 2060]
    # fully_connected_time = [156058, 155034]
    # convolution_time = [237248, 236994]
    # ys = [dot_product_time, fully_connected_time, convolution_time]
    # save_path = os.path.join(args.odir, "pipelined_startup.png")
    # plot_time(functions, ys, "", "Functions", ylables, save_path)

    # plot for optimazation: pipelined start-up
    categories = ["Dot Product", "Fully Connected", "Convolution"]
    no_optimization = [2060, 156058, 237248]
    pipelined_startup = [2060, 155034, 236994]
    values = [v1 - v2 for v1, v2 in zip(no_optimization, pipelined_startup)]
    save_path = os.path.join(args.odir, "pipelined_startup_hist.png")
    hist_time(categories, values, 'Function', 'Reduced Time (cycles)', save_path)



