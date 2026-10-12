#!/usr/bin/env python3
"""Render portable SVG score charts from calculate_score.py JSON output.

Uses only the Python standard library. Pie slices show each dimension's share of
points earned (not its completion percentage); the bar chart shows score / max.
"""
import argparse
import html
import json
import math
from pathlib import Path

PALETTE = ["#2563eb", "#ea580c", "#16a34a", "#9333ea", "#0891b2"]
FONT = "Arial, 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif"


def read_record(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    dims = data.get("dimensions")
    if not isinstance(dims, list) or len(dims) != 5:
        raise ValueError("score record must contain five scored dimensions")
    rows = []
    for item in dims:
        name, score, maximum = item.get("name"), item.get("raw_score"), item.get("max_score")
        if not isinstance(name, str) or not isinstance(score, (int, float)) or not isinstance(maximum, (int, float)) or maximum <= 0 or score < 0:
            raise ValueError("invalid dimension data")
        rows.append((name, float(score), float(maximum)))
    return rows, float(data.get("raw_score", sum(x[1] for x in rows)))


def svg_start(width, height, title, description):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description)}</desc>
<style>text{{font-family:{FONT};fill:#172033}} .muted{{fill:#64748b}} .grid{{stroke:#dbe2ea;stroke-width:1}} .axis{{stroke:#64748b;stroke-width:1.2}}</style>
<rect width="100%" height="100%" fill="#ffffff"/>
''']


def bar_chart(rows):
    width, height = 960, 440
    left, right, top, bottom = 285, 115, 90, 70
    plot_w, plot_h = width-left-right, height-top-bottom
    row_gap = plot_h/len(rows)
    out = svg_start(width, height, "五维评分柱状图", "各维度得分及满分；柱长表示该维度得分占本维度满分的比例。")
    out.append('<text x="40" y="45" font-size="26" font-weight="700">五维评分</text>')
    for pct in (0,25,50,75,100):
        x=left+plot_w*pct/100
        out.append(f'<line class="grid" x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{height-bottom+4}"/>')
        out.append(f'<text class="muted" x="{x:.1f}" y="{height-bottom+27}" font-size="13" text-anchor="middle">{pct}%</text>')
    total=0
    for i,(name,score,maximum) in enumerate(rows):
        y=top+row_gap*(i+.5)
        pct=score/maximum
        total += score
        out.append(f'<text x="{left-18}" y="{y+6:.1f}" font-size="17" text-anchor="end">{html.escape(name)}</text>')
        out.append(f'<rect x="{left}" y="{y-15:.1f}" width="{plot_w}" height="30" rx="7" fill="#eef2f7"/>')
        out.append(f'<rect x="{left}" y="{y-15:.1f}" width="{plot_w*pct:.1f}" height="30" rx="7" fill="{PALETTE[i]}"/>')
        out.append(f'<text x="{width-32}" y="{y+6:.1f}" font-size="16" font-weight="700" text-anchor="end">{score:g} / {maximum:g}</text>')
    out.append(f'<text class="muted" x="40" y="{height-22}" font-size="14">总分：{total:.1f} / 100 · 柱长表示维度得分率</text>')
    out.append('</svg>')
    return ''.join(out)


def donut_chart(rows, total):
    width, height = 960, 520
    cx, cy, radius = 250, 270, 160
    out=svg_start(width,height,"各维度实得分构成饼图","饼图显示各维度得分占总实得分的比例，不表示各维度完成率。")
    out.append('<text x="40" y="45" font-size="26" font-weight="700">各维度实得分构成</text>')
    if total <= 0:
        out.append('<text x="250" y="270" text-anchor="middle" font-size="18">暂无可绘制得分</text>')
    else:
        angle=-math.pi/2
        for i,(name,score,maximum) in enumerate(rows):
            if score <= 0: continue
            delta=2*math.pi*score/total
            start=(cx+radius*math.cos(angle),cy+radius*math.sin(angle))
            end=(cx+radius*math.cos(angle+delta),cy+radius*math.sin(angle+delta))
            large=1 if delta>math.pi else 0
            if delta >= 2*math.pi-1e-8:
                mid=(cx-radius,cy)
                d=f'M {cx} {cy-radius} A {radius} {radius} 0 1 1 {mid[0]} {mid[1]} A {radius} {radius} 0 1 1 {cx} {cy-radius} Z'
            else:
                d=f'M {cx} {cy} L {start[0]:.2f} {start[1]:.2f} A {radius} {radius} 0 {large} 1 {end[0]:.2f} {end[1]:.2f} Z'
            out.append(f'<path d="{d}" fill="{PALETTE[i]}" stroke="#ffffff" stroke-width="2"><title>{html.escape(name)}：{score:g}分，占实得总分 {score/total*100:.1f}%</title></path>')
            angle += delta
        out.append(f'<circle cx="{cx}" cy="{cy}" r="92" fill="#ffffff"/>')
        out.append(f'<text x="{cx}" y="{cy-4}" font-size="31" font-weight="700" text-anchor="middle">{total:.1f}</text>')
        out.append(f'<text class="muted" x="{cx}" y="{cy+24}" font-size="15" text-anchor="middle">总分 / 100</text>')
    x0,y0=490,130
    for i,(name,score,maximum) in enumerate(rows):
        y=y0+i*66
        share=(score/total*100) if total>0 else 0
        out.append(f'<rect x="{x0}" y="{y-18}" width="20" height="20" rx="4" fill="{PALETTE[i]}"/>')
        out.append(f'<text x="{x0+34}" y="{y-2}" font-size="17" font-weight="600">{html.escape(name)}</text>')
        out.append(f'<text class="muted" x="{x0+34}" y="{y+22}" font-size="15">得分 {score:g}/{maximum:g} · 占实得总分 {share:.1f}%</text>')
    out.append('<text class="muted" x="40" y="490" font-size="14">口径：各维度实得分 ÷ 总实得分；请勿将饼图百分比解读为维度完成率。</text>')
    out.append('</svg>')
    return ''.join(out)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score_record", help="JSON output from calculate_score.py")
    parser.add_argument("--output-dir", default="charts", help="Directory for SVG files")
    args=parser.parse_args()
    rows,total=read_record(args.score_record)
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    (out/"dimension-scores.svg").write_text(bar_chart(rows),encoding="utf-8")
    (out/"score-composition.svg").write_text(donut_chart(rows,total),encoding="utf-8")
    print(f"Wrote {out/'dimension-scores.svg'} and {out/'score-composition.svg'}")

if __name__ == "__main__":
    main()
