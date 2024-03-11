import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
import seaborn as sns
from matplotlib.legend_handler import HandlerTuple
import os
import pandas as pd


# Function to extract log data from a file
def extract_log_data(logfile):
    with open(logfile, "r") as f:
        log_data = f.readlines()
    log_data = [x.strip() for x in log_data]
    log_data = [
        [x[:26], x[28:35].strip(), x[38:39], x[41:]] for x in log_data if x != ""
    ]
    log_data = pd.DataFrame(
        log_data, columns=["timestamp", "thread", "level", "message"]
    )
    return log_data


# Function to extract measurement data from log data
def get_measurement_data(logfile):
    log_data = extract_log_data(logfile)
    log_data = log_data[
        log_data["message"].str.contains("MEAS:  New measurement", na=False)
    ]
    log_data[["measurement_type", "earfcn", "pci", "rsrp", "cfo"]] = (
        log_data.message.str.extract(
            r"MEAS:  New measurement (serving|neighbour) cell: earfcn=(.*), pci=(.*), rsrp=(.*) dBm, cfo=(.*) Hz"
        )
    )
    log_data = log_data[["timestamp", "measurement_type", "pci", "rsrp"]]
    log_data["timestamp"] = pd.to_datetime(log_data["timestamp"])
    log_data["pci"] = log_data["pci"].astype(int)
    log_data["rsrp"] = log_data["rsrp"].astype(float)
    return log_data


# Function to smooth RSRP values within each PCI
def smoothed_rsrp(log_data, window_ms=50):
    cells = []
    # smooth rsrp values within each pci
    smooth_data = log_data.copy()
    smooth_data.set_index("timestamp", inplace=True)
    for pci in log_data.pci.unique():
        smooth_data.loc[smooth_data.pci == pci, "rsrp"] = (
            smooth_data.loc[smooth_data.pci == pci, "rsrp"]
            .rolling(window=f"{window_ms}ms")
            .mean()
        )

    smooth_data.reset_index(inplace=True)
    return smooth_data


# Custom legend handler to combine rectangle and line
class PCILegendHandler(HandlerTuple):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        rect: mpl.patches.Rectangle = orig_handle[0]
        line: mpl.lines.Line2D = orig_handle[1]
        # Adjust the position and size of the line
        line.set_transform(trans)

        # Add the white line before line
        line_white = mpl.lines.Line2D((0.5, 1), (0.5, 0.5), color="white")
        line.set_xdata([0.1 * width, 0.9 * width])
        line.set_ydata([0.5 * height, 0.5 * height])
        rect.set_transform(trans)
        # Adjust the position and size of the rectangle
        # rect.set_transform(trans)
        rect.set_xy([0.08 * width, 0])
        rect.set_width(0.83 * width)
        rect.set_height(1 * height)

        artists = (rect, line, line_white)
        return artists


def plot_current_cell(log_data, ax, area_cmap):
    # Show current serving cell
    serving_cell = log_data[log_data["measurement_type"] == "serving"]
    pcis_labelled = []
    # Shade in background to indicate serving cell's pci
    current_pci = serving_cell["pci"].values[0]
    current_timestamp = serving_cell["timestamp"].values[0]
    for i, row in serving_cell.iterrows():
        if row["pci"] != current_pci:
            if current_pci not in pcis_labelled:
                pcis_labelled.append(current_pci)
                ax.axvspan(
                    current_timestamp,
                    row["timestamp"],
                    color=area_cmap[current_pci],
                    alpha=0.2,
                )
            else:
                ax.axvspan(
                    current_timestamp,
                    row["timestamp"],
                    color=area_cmap[current_pci],
                    alpha=0.2,
                )
            current_pci = row["pci"]
            current_timestamp = row["timestamp"]
    if current_pci not in pcis_labelled:
        pcis_labelled.append(current_pci)
        ax.axvspan(
            current_timestamp,
            row["timestamp"],
            color=area_cmap[current_pci],
            alpha=0.2,
        )
    else:
        ax.axvspan(
            current_timestamp, row["timestamp"], color=area_cmap[current_pci], alpha=0.2
        )


# Function to plot RSRP vs Time
def plot_rsrp_vs_time(
    logfile,
    smooth_rsrp_ms=None,
    print_handover=False,
    title="RSRP vs Time",
    ax=None,
    show=True,
):
    log_data = get_measurement_data(logfile)
    if smooth_rsrp_ms is not None:
        log_data = smoothed_rsrp(log_data, window_ms=smooth_rsrp_ms)
    else:
        log_data = log_data
    n_pci = log_data["pci"].nunique()
    line_cmap = sns.color_palette()[
        min(log_data["pci"].unique()) : n_pci + min(log_data["pci"].unique())
    ]
    area_cmap = sns.color_palette("pastel")
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        x="timestamp", y="rsrp", data=log_data, hue="pci", palette=line_cmap, ax=ax
    )
    plt.title(title)
    plot_current_cell(log_data, ax, area_cmap)
    # Customize the legend
    handles, labels = ax.get_legend_handles_labels()
    new_handles = []
    new_labels = []

    # Iterate through each handle and label
    for handle, label in zip(handles, labels):
        # Extract the color of the line
        color = handle.get_color()

        # Create a new rectangle with the same color as the line
        rect = plt.Rectangle(
            (0, 0), 1, 1, fc=area_cmap[int(label)], ec=area_cmap[int(label)]
        )
        line = plt.Line2D((0, 1), (0.5, 0.5), color=color)
        combined_handle = (rect, line)
        new_handles.append(combined_handle)
        new_labels.append(f"PCI {label}")

    ax.legend(
        handles=new_handles,
        labels=new_labels,
        loc="upper left",
        handler_map={tuple: PCILegendHandler()},
    )
    if show:
        plt.show()


# Function to plot Throughput vs Time
def plot_throughput_vs_time(
    pcap_file,
    smooth_throughput_ms=100,
    title="Throughput vs Time",
    ax=None,
    show=True,
    logfile=None,
):
    throughput = pd.read_csv(pcap_file)  # Convert packets to a DataFrame

    # Rest of your code...
    throughput["timestamp"] = pd.to_datetime(throughput["frame.time_epoch"], unit="s")
    throughput.set_index("timestamp", inplace=True)

    throughput["length"] = throughput["frame.len"]
    throughput["udp.dstport"] = throughput["udp.dstport"].astype(int, errors="ignore")
    throughput = throughput[throughput["udp.dstport"] == 5201]
    throughput = throughput[["length"]]
    # Set length from bytes to Mbits

    throughput = (
        throughput.resample(f"{smooth_throughput_ms}ms").sum()
        * 1000
        / smooth_throughput_ms
    )

    throughput["length"] = throughput["length"] * 8 / 1e6

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlabel("Time")
    ax.set_ylabel("Throughput (Mbit/s)")
    ax.plot(
        throughput.index,
        throughput["length"],
        c="black",  # sns.color_palette()[7],
        alpha=0.7,
        # linestyle="dashdot",
    )

    if logfile is not None:
        log_data = get_measurement_data(logfile)
        plot_current_cell(log_data, ax, sns.color_palette("pastel"))
    ax.set_title(title)

    ax.legend(["Throughput"], loc="upper right")

    if show:
        plt.show()


# Function to plot RSRP and Throughput vs Time
def plot_experiment(
    logfile,
    pcapfile,
    title="RSRP/Throughput vs Time",
    from_time=None,
    to_time=None,
    smooth_rsrp_ms=1000,
    smooth_throughput_ms=100,
):

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_rsrp_vs_time(
        logfile,
        print_handover=False,
        title=title,
        ax=ax,
        show=False,
        smooth_rsrp_ms=smooth_rsrp_ms,
    )
    ax2 = ax.twinx()
    # make sure ax2 is plotted lower than ax so plots do not intersect
    ax2.set_zorder(ax.get_zorder() - 1)
    ax.patch.set_visible(False)

    plot_throughput_vs_time(
        pcapfile,
        title="",
        ax=ax2,
        show=False,
        smooth_throughput_ms=smooth_throughput_ms,
    )

    # Limit the time range
    if from_time is not None and to_time is not None:
        # convert from HH:MM:SS to datetime, get the first date from the log data
        with open(logfile, "r") as f:
            day = f.readline()[:10]
        from_time = pd.to_datetime(f"{day} {from_time}")
        to_time = pd.to_datetime(f"{day} {to_time}")
        ax.set_xlim(from_time, to_time)
        ax2.set_xlim(from_time, to_time)
    plt.show()


# Function to plot RSRP and Throughput vs Time
def plot_experiment_subplots(
    logfile,
    pcapfile,
    title="RSRP/Throughput vs Time",
    from_time=None,
    to_time=None,
    smooth_rsrp_ms=1000,
    smooth_throughput_ms=100,
):

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    plt.subplots_adjust(hspace=0)

    plot_rsrp_vs_time(
        logfile,
        print_handover=False,
        title="",
        ax=ax1,
        show=False,
        smooth_rsrp_ms=smooth_rsrp_ms,
    )

    plot_throughput_vs_time(
        pcapfile,
        title="",
        ax=ax2,
        show=False,
        smooth_throughput_ms=smooth_throughput_ms,
        logfile=logfile,
    )

    fig.suptitle(title)

    # Limit the time range
    if from_time is not None and to_time is not None:
        # convert from HH:MM:SS to datetime, get the first date from the log data
        with open(logfile, "r") as f:
            day = f.readline()[:10]
        from_time = pd.to_datetime(f"{day} {from_time}")
        to_time = pd.to_datetime(f"{day} {to_time}")
        ax1.set_xlim(from_time, to_time)
        ax2.set_xlim(from_time, to_time)

    plt.show()
