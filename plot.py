from dateutil.relativedelta import relativedelta
import csv
from datetime import date, datetime
from pathlib import Path

import matplotlib.pyplot as plt

h = 20
w = 25
label_width = 450
day0 = date(2020, 7, 1)

file_names = [
    "controller-metrics.csv",
    "perception.csv",
    "rl.csv",
]

colors = [
    "c",
    "m",
    "y",
]


def to_date(string):
    return date(*map(int, string.split("-")))


def values_generator():
    for file_name, color in zip(file_names, colors):
        with Path("L2M Gantt - " + file_name).open() as f:
            reader = csv.reader(f)
            subgroup = next(reader)[0]
            next(reader)  # header
            for row in reader:
                label, start, end = row
                start = to_date(start)
                end = to_date(end)
                yield label, start, end, subgroup, color


values = sorted(values_generator(), key=lambda t: t[1], reverse=True)


def days_elapsed():
    for (label, start, end, _, _) in values:
        yield (end - day0).days


total_width = label_width + max(days_elapsed())
ymax = len(values) - 1
fontsize = 16


def plot(highlight, out_name=None):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, total_width)

    for y, (label, start, end, subgroup, color) in enumerate(values):
        alpha = 1 if color in highlight else 0.2
        width = (end - start).days
        left = label_width + (start - day0).days
        ax.text(
            x=0,
            y=y,
            s=" " + label,
            ha="left",
            wrap=True,
            alpha=alpha,
            fontsize=fontsize,
            va="center",
        )
        ax.barh(
            y=y, width=total_width, height=1, left=0, color="grey", alpha=(y % 2) * 0.1
        )
        ax.barh(
            y=y,
            width=width,
            height=0.7,
            left=left,
            color=color,
            label=subgroup,
            alpha=alpha,
        )

    x = label_width + (datetime.now().date() - day0).days
    ax.vlines(x, ymin=-1, ymax=ymax, color="k")

    for i in range(16):
        month = day0 + relativedelta(months=i)
        days = (month - day0).days
        x = label_width + days
        ax.axvline(x, color="grey", linestyle=":")
        ax.text(x=x, y=len(values), s=f"M{i}", fontsize=fontsize)
        ax.text(x=x, y=1 + len(values), s=month.strftime("%b"), fontsize=fontsize)

    handles, labels = ax.get_legend_handles_labels()
    indexes = [labels.index(l) for l in set(labels)]
    handles = [handles[i] for i in indexes]
    labels = [labels[i] for i in indexes]
    ax.legend(handles, labels, loc="right", fontsize=fontsize)
    ax.axis("off")
    print(out_name, highlight)
    plt.tight_layout()
    if out_name:
        plt.savefig(out_name)
    else:
        plt.show()
    plt.close()


if __name__ == '__main__':
    for args in [
        ("c", "controller"),
        ("m", "perception"),
        ("y", "rl"),
        ("cmy", "full"),
    ]:
        plot(*args)
