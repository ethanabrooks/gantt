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
    "perception.csv",
    "rl.csv",
    "controller-metrics.csv",
]

colors = [
    "darkgreen",
    "darkblue",
    "darkviolet",
]


def subgroups_gen():
    for file_name in file_names:
        with Path("L2M Gantt - " + file_name).open() as f:
            reader = csv.reader(f)
            yield next(reader)[0]


subgroups = list(subgroups_gen())


def to_date(string):
    return date(*map(int, string.split("-")))


def file_values(file_name):
    with Path("L2M Gantt - " + file_name).open() as f:
        reader = csv.reader(f)
        next(reader)
        next(reader)  # header
        for row in reader:
            label, start, end = row
            label = label.strip(".") + "."
            start = to_date(start)
            end = to_date(end)
            yield label, start, end


def gen():
    for file_name, subgroup, color in zip(file_names, subgroups, colors):
        for value in sorted(file_values(file_name), key=lambda t: t[1], reverse=True):
            yield tuple((*value, color))
        yield subgroup, None, None, color


values = list(gen())


def days_elapsed():
    for (label, start, end, *_) in values:
        if end is not None:
            yield (end - day0).days


total_width = label_width + max(days_elapsed())
ymax = len(values) - 1
fontsize = 16


def plot(highlight, out_name=None):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, total_width)

    for y, (label, start, end, color) in enumerate(values):
        ax.barh(
            y=y, width=total_width, height=1, left=0, color="grey", alpha=(y % 2) * 0.1
        )
        alpha = 1 if color in highlight else 0.2
        if None in (start, end):
            assert start == end
            ax.text(
                x=0,
                y=y,
                s=" " + label,
                ha="left",
                wrap=True,
                alpha=alpha,
                fontsize=fontsize,
                fontweight='bold',
                color="black",
                va="center",
            )
        else:
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
                color=color,
                va="center",
            )
            ax.barh(
                y=y,
                width=width,
                height=0.7,
                left=left,
                color=color,
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

    ax.axis("off")
    print(out_name, highlight)
    plt.tight_layout()
    if out_name:
        plt.savefig(out_name)
    else:
        plt.show()
    plt.close()


if __name__ == "__main__":
    for args in [
        (["darkgreen"], "controller"),
        (["darkblue"], "perception"),
        (["darkviolet"], "rl"),
        (["darkgreen", "darkblue", "darkviolet"], "full"),
    ]:
        plot(*args)
