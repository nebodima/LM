"""Exact flat geometry shared by SVG originals and transparent PNG exports.

Only writes inside this icon directory. Requires Pillow; no external renderer.
"""
from __future__ import annotations
import math
import re
from html import escape
from PIL import Image, ImageDraw

T = '#1E9E8F'
S = '#34495E'
Y = '#F5B642'
L = '#E9F5F3'
R = '#C94E48'


class Canvas:
    def __init__(self, size):
        self.size = size
        self.scale = 16 if size == 16 else 32
        self.image = Image.new('RGBA', (size*self.scale, size*self.scale))
        self.draw = ImageDraw.Draw(self.image)
        self.svg = []

    def _point(self, point):
        return tuple(round(v*self.scale) for v in point)

    def circle(self, x, y, radius, fill, stroke=None, sw=1):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" {self._style(fill, stroke, sw)}/>')
        bounds = self._point((x-radius, y-radius, x+radius, y+radius))
        self.draw.ellipse(bounds, fill=fill)
        if stroke:
            self._stroke([(x+radius*math.cos(a*math.tau/160), y+radius*math.sin(a*math.tau/160)) for a in range(161)], stroke, sw)

    def rr(self, x, y, width, height, radius, fill, stroke=None, sw=1):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" {self._style(fill, stroke, sw)}/>')
        points=[]
        radius=min(radius, width/2, height/2)
        for cx,cy,angle in [(x+width-radius,y+radius,-90),(x+width-radius,y+height-radius,0),(x+radius,y+height-radius,90),(x+radius,y+radius,180)]:
            for step in range(17):
                theta=math.radians(angle+step*90/16)
                points.append((cx+radius*math.cos(theta),cy+radius*math.sin(theta)))
        points.append(points[0])
        if fill:
            self.draw.polygon([self._point(p) for p in points], fill=fill)
        if stroke:
            self._stroke(points,stroke,sw)

    def poly(self, points, fill, stroke=None, sw=1):
        self.svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" {self._style(fill,stroke,sw)}/>')
        if fill:
            self.draw.polygon([self._point(p) for p in points],fill=fill)
        if stroke:
            self._stroke(list(points)+[points[0]],stroke,sw)

    def line(self, points, color=S, width=1.5):
        self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" {self._style(None,color,width)}/>')
        self._stroke(points,color,width)

    def _stroke(self, points, color, width):
        scaled=[self._point(p) for p in points]
        self.draw.line(scaled,fill=color,width=round(width*self.scale),joint='curve')
        radius=width*self.scale/2
        # Round caps/joins are identical to SVG's specified stroke style.
        for x,y in scaled:
            self.draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color)

    def path(self, data, fill=None, stroke=None, sw=1.5):
        self.svg.append(f'<path d="{escape(data)}" {self._style(fill,stroke,sw)}/>')
        tokens=re.findall(r'[MLHVQCZ]|-?\d*\.?\d+(?:[eE][-+]?\d+)?',data)
        index=0
        current=(0,0)
        points=[]
        def flush():
            if len(points)>1:
                if fill:
                    self.draw.polygon([self._point(p) for p in points],fill=fill)
                if stroke:
                    self._stroke(points,stroke,sw)
        while index<len(tokens):
            command=tokens[index]
            index+=1
            count={'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6,'Z':0}[command]
            values=[float(v) for v in tokens[index:index+count]]
            index+=count
            if command=='M':
                flush(); points=[]; current=tuple(values); points.append(current)
            elif command in ('L','H','V'):
                current=tuple(values) if command=='L' else ((values[0],current[1]) if command=='H' else (current[0],values[0]))
                points.append(current)
            elif command in ('Q','C'):
                start=current
                for step in range(1,49):
                    t=step/48; u=1-t
                    if command=='Q':
                        point=tuple(u*u*start[d]+2*u*t*values[d]+t*t*values[d+2] for d in (0,1))
                    else:
                        point=tuple(u**3*start[d]+3*u*u*t*values[d]+3*u*t*t*values[d+2]+t**3*values[d+4] for d in (0,1))
                    points.append(point)
                current=points[-1]
            elif command=='Z':
                points.append(points[0]); current=points[0]
        flush()

    @staticmethod
    def _style(fill, stroke, width):
        return f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'

    def save(self, svg_path, png_path, pixels):
        svg_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+f'<svg xmlns="http://www.w3.org/2000/svg" width="{pixels}" height="{pixels}" viewBox="0 0 {self.size} {self.size}">\n'+'\n'.join(self.svg)+'\n</svg>\n',encoding='utf-8')
        self.image.resize((pixels,pixels),Image.Resampling.LANCZOS).save(png_path,optimize=True)


def icon(name, label, description, usage, small, large):
    return dict(name='УЗ_И'+name,label=label,description=description,usage=usage,small=small,large=large)
