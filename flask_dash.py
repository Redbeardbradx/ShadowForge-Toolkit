#!/usr/bin/env python3
from flask import Flask, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/horde')
def horde_pie():
    df = pd.read_csv('reports/scan_log.csv')
    counts = df['command'].value_counts()
    fig, ax = plt.subplots()
    counts.plot.pie(ax=ax, autopct='%1.1f%%')
    ax.set_title('Horde Commands Pie—ShadowForge Grind')
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template_string('<h1>Horde Pie</h1><img src="data:image/png;base64,{{ plot }}">', plot=plot_url)

@app.route('/')
def home():
    return '<h1>ShadowForge Dash—Horde Viz</h1><a href="/horde">Horde Pie</a>'

if __name__ == '__main__':
    app.run(debug=True, port=5001)