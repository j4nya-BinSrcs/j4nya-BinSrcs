import re
import sys


def luminance(r, g, b):
    return round(0.2126 * r + 0.7152 * g + 0.0722 * b)


def main(path):
    s = open(path).read()

    def to_grey(m):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        l = luminance(r, g, b)
        return f"rgb({l}, {l}, {l})"

    s = re.sub(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", to_grey, s)

    s = re.sub(
        r"\.radar\s*\{[^}]*\}",
        ".radar {\n"
        "stroke-width: 4px;\n"
        "stroke: #9a9a9a;\n"
        "fill: #9a9a9a;\n"
        "fill-opacity: 0.5;\n"
        "animation: rad-gs 10s linear infinite;\n"
        "}\n"
        "@keyframes rad-gs {"
        "0.00%{fill:rgb(150,150,150);stroke:rgb(150,150,150)}"
        "50.00%{fill:rgb(240,240,240);stroke:rgb(240,240,240)}"
        "100.00%{fill:rgb(150,150,150);stroke:rgb(150,150,150)}}",
        s,
        count=1,
    )

    open(path, "w").write(s)


if __name__ == "__main__":
    main(sys.argv[1])