# 📸 Screenshot Guide for LaTeX Submission

This guide helps you capture perfect screenshots for your report and presentation.

## 🎯 Required Screenshots

### Essential Screenshots (Priority 1)

| # | Screenshot Name | Dashboard Tab | What to Show | File Name |
|---|----------------|---------------|--------------|-----------|
| 1 | Price Chart | Price Chart | Candlestick + MA + BB + Volume | `dashboard_price.png` |
| 2 | Technical Indicators | Technical Indicators | RSI + MACD charts | `dashboard_indicators.png` |
| 3 | AI Predictions | AI Predictions | 4-model comparison chart | `dashboard_predictions.png` |
| 4 | News Sentiment | News & Sentiment | Timeline + news feed | `dashboard_sentiment.png` |
| 5 | Correlation | Correlation Analysis | Heatmap | `dashboard_correlation.png` |
| 6 | Portfolio | Portfolio | Holdings table + metrics | `dashboard_portfolio.png` |

### Additional Screenshots (Priority 2)

| # | Screenshot Name | What to Show | File Name |
|---|----------------|--------------|-----------|
| 7 | Full Dashboard | Home page with all tabs visible | `dashboard_full.png` |
| 8 | Settings Sidebar | Left sidebar with all options | `dashboard_sidebar.png` |
| 9 | Metrics Cards | Top metrics row | `dashboard_metrics.png` |

## 🚀 Quick Start

### 1. Start the Dashboard

```bash
cd /home/lol/big_btata/MarketPulse
streamlit run dashboard/enhanced_app.py
```

Wait for the message:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 2. Open in Browser

```bash
# Linux
xdg-open http://localhost:8501

# Or manually open browser and go to:
http://localhost:8501
```

### 3. Recommended Settings

For best screenshots:

**In Dashboard Sidebar:**
- Market: International Markets (more data available)
- Symbol: AAPL or GOOGL
- Time Range: 3M (3 months)
- Chart Type: Candlestick
- Enable: Volume, Moving Averages, Bollinger Bands, Indicators

**Browser:**
- Use Chrome or Firefox
- Zoom: 100% (Ctrl+0)
- Window: Maximized
- Theme: Dashboard's dark theme

## 📸 Step-by-Step Screenshot Process

### Screenshot 1: Price Chart Tab

**Setup:**
1. Click "Price Chart" tab
2. Select symbol: AAPL
3. Time range: 3M
4. Enable all options in sidebar:
   - ✓ Show Volume
   - ✓ Show Moving Averages
   - ✓ Show Bollinger Bands

**What should be visible:**
- Candlestick chart with green/red candles
- Orange SMA 20 line
- Blue SMA 50 line
- Gray Bollinger Bands (upper and lower)
- Volume bars at bottom
- Any red X markers (anomalies)

**Capture:**
- Press F11 for fullscreen (optional)
- Take screenshot: `Ctrl+Shift+Print` (Linux) or use screenshot tool
- Save as: `figures/dashboard_price.png`
- Exit fullscreen: F11

### Screenshot 2: Technical Indicators Tab

**Setup:**
1. Click "Technical Indicators" tab
2. Same symbol (AAPL)
3. Ensure indicators are calculated

**What should be visible:**
- RSI chart showing line oscillating between 0-100
- Red horizontal line at 70 (overbought)
- Green horizontal line at 30 (oversold)
- MACD histogram (green/red bars)
- Indicator values in cards or table
- Indicator guide (if expanded)

**Capture:**
- Take screenshot
- Save as: `figures/dashboard_indicators.png`

### Screenshot 3: AI Predictions Tab

**Setup:**
1. Click "AI Predictions" tab
2. Wait for predictions to load

**What should be visible:**
- Line chart with multiple colored lines:
  - Blue: LSTM
  - Green: GRU
  - Orange: Transformer
  - Red/Bold: Ensemble
- Legend showing all models
- Prediction metrics table showing:
  - RMSE, MAE, R², Directional Accuracy for each model
- 7-day forecast table with dates and prices
- Confidence metrics

**Capture:**
- Ensure all 4-5 lines are visible
- Save as: `figures/dashboard_predictions.png`

### Screenshot 4: News & Sentiment Tab

**Setup:**
1. Click "News & Sentiment" tab
2. Scroll to show both sections

**What should be visible:**
- Top section: Sentiment timeline chart
  - Price line (cyan)
  - Scatter points colored by sentiment (green/red/gray)
  - Overlay showing how news correlates with price
- Bottom section: News feed
  - Headlines with sentiment indicators (🟢🔴🟡)
  - Sentiment scores
  - Timestamps
  - Relevance percentages
- Sentiment distribution (bar chart or metrics)

**Capture:**
- May need to take 2 screenshots and combine, or
- Zoom out slightly (Ctrl+- once) to fit more
- Save as: `figures/dashboard_sentiment.png`

### Screenshot 5: Correlation Analysis Tab

**Setup:**
1. Click "Correlation Analysis" tab
2. Make sure heatmap is visible

**What should be visible:**
- Correlation heatmap/matrix
  - Color-coded cells (red=negative, blue=positive)
  - Stock symbols on axes
  - Correlation values in cells (-1 to +1)
- Sector distribution pie chart (optional)
- Legend explaining colors

**Capture:**
- Save as: `figures/dashboard_correlation.png`

### Screenshot 6: Portfolio Tab

**Setup:**
1. Click "Portfolio" tab
2. If empty, add a few positions:
   - Symbol: AAPL, Shares: 10, Avg Price: 150
   - Symbol: GOOGL, Shares: 5, Avg Price: 140

**What should be visible:**
- Portfolio holdings table with columns:
  - Symbol, Shares, Avg Price, Current Price, Value, Gain/Loss, Return %
- Total portfolio metrics:
  - Total Value
  - Total Cost
  - Total Return ($ and %)
- Add position form/button
- Color coding (green for gains, red for losses)

**Capture:**
- Save as: `figures/dashboard_portfolio.png`

## 🛠️ Screenshot Tools

### Linux

**Option 1: GNOME Screenshot (Pre-installed)**
```bash
gnome-screenshot -a  # Area selection
gnome-screenshot -w  # Current window
gnome-screenshot     # Full screen
```

**Option 2: Flameshot (Better)**
```bash
sudo apt-get install flameshot
flameshot gui  # Launch screenshot tool
```

**Option 3: Scrot**
```bash
sudo apt-get install scrot
scrot -s filename.png  # Select area
```

### macOS

**Built-in:**
- `Cmd + Shift + 4`: Select area
- `Cmd + Shift + 3`: Full screen
- `Cmd + Shift + 5`: Screenshot utility

### Windows

**Built-in:**
- `Win + Shift + S`: Snipping tool
- Or use "Snip & Sketch" app

## 🎨 Screenshot Quality Tips

### Before Taking Screenshot

1. **Clean up browser:**
   - Close unnecessary tabs
   - Hide bookmarks bar (Ctrl+Shift+B)
   - Full screen (F11) for cleaner capture

2. **Wait for loading:**
   - Ensure all charts are fully rendered
   - No loading spinners visible
   - Data is populated

3. **Adjust view:**
   - Zoom to 100% (Ctrl+0)
   - Maximize window
   - Scroll to show relevant section

### During Screenshot

1. **Frame correctly:**
   - Include relevant UI elements
   - Don't cut off important parts
   - Leave small margins

2. **Timing:**
   - Wait for animations to finish
   - Capture when chart is stable
   - No hover effects unless intentional

### After Taking Screenshot

1. **Check quality:**
   - Clear and readable
   - No blur
   - Good contrast
   - Text is legible

2. **File format:**
   - Save as PNG (not JPG)
   - High resolution (1920x1080 or higher)
   - File size: 100KB - 2MB per screenshot

3. **Naming:**
   - Use exact names from guide
   - All lowercase
   - Underscores not spaces
   - .png extension

## 📁 File Organization

Save all screenshots in the `figures/` directory:

```
latex-submission/
└── figures/
    ├── dashboard_price.png           ✓ Screenshot 1
    ├── dashboard_indicators.png      ✓ Screenshot 2
    ├── dashboard_predictions.png     ✓ Screenshot 3
    ├── dashboard_sentiment.png       ✓ Screenshot 4
    ├── dashboard_correlation.png     ✓ Screenshot 5
    ├── dashboard_portfolio.png       ✓ Screenshot 6
    └── [additional screenshots]
```

## 🔄 Workflow

Recommended workflow for efficiency:

```bash
# 1. Start dashboard
streamlit run dashboard/enhanced_app.py

# 2. Open browser
# Go to http://localhost:8501

# 3. Set up screenshot tool
flameshot gui  # Or your preferred tool

# 4. For each tab (in order):
#    - Navigate to tab
#    - Configure settings
#    - Wait for rendering
#    - Take screenshot
#    - Save with correct name
#    - Move to next tab

# 5. Verify all screenshots
ls -lh figures/*.png

# 6. Update LaTeX files with screenshots

# 7. Compile to check
./compile.sh
```

## ✅ Verification Checklist

Before considering screenshots complete:

- [ ] All 6 essential screenshots captured
- [ ] Files saved in `figures/` directory
- [ ] Correct file names (match guide exactly)
- [ ] PNG format (not JPG)
- [ ] High resolution (check file size: 200KB-2MB each)
- [ ] All text is readable
- [ ] Charts are fully visible
- [ ] No loading spinners or errors visible
- [ ] Colors look good
- [ ] Opened each file to verify it displays correctly

## 🔧 Troubleshooting

### Problem: Dashboard not loading

**Solution:**
```bash
# Kill existing streamlit
pkill -f streamlit

# Restart
streamlit run dashboard/enhanced_app.py
```

### Problem: Charts not rendering

**Solution:**
- Wait 5-10 seconds after navigation
- Refresh browser (F5)
- Clear browser cache (Ctrl+Shift+Delete)
- Try different browser

### Problem: Screenshot too large/small

**Solution:**
- Use browser zoom: Ctrl+0 (reset), Ctrl++ (zoom in), Ctrl+- (zoom out)
- Resize browser window
- Use screenshot tool's selection mode

### Problem: Colors look wrong

**Solution:**
- Dashboard uses dark theme by default
- Ensure browser is in normal mode (not dark mode override)
- Check monitor color settings

### Problem: Text blurry in screenshot

**Solution:**
- Take screenshot at higher resolution
- Don't scale browser window too small
- Use PNG not JPG
- Disable browser's font smoothing

## 💡 Pro Tips

1. **Consistency:** Use same symbol (AAPL) for all screenshots for cohesive look

2. **Data richness:** 3M or 6M time range shows good amount of data

3. **Aspect ratio:** Landscape orientation (horizontal) works best for reports

4. **File size:** If PNG is too large, use:
   ```bash
   optipng dashboard_price.png  # Optimize PNG
   ```

5. **Batch editing:** Use GIMP or ImageMagick for batch processing if needed:
   ```bash
   # Resize all to width 1920px
   mogrify -resize 1920x figures/*.png
   ```

6. **Dark theme:** Dashboard's dark theme looks professional in reports

7. **Annotations:** Use GIMP or Inkscape to add arrows/labels if needed

## 🎬 Video Alternative

If screenshots are difficult, consider:

1. Record screen video of dashboard tour
2. Extract high-quality frames using:
   ```bash
   ffmpeg -i dashboard_demo.mp4 -vf "select='eq(n,100)'" -vsync 0 screenshot.png
   ```

## 📚 Additional Resources

- **Image editing:** GIMP (free Photoshop alternative)
- **Batch processing:** ImageMagick command-line tool
- **Screenshots in LaTeX:** Use `\includegraphics[width=0.9\textwidth]{figures/name.png}`

---

**Ready to take screenshots? Follow this guide step-by-step for perfect results!** 📸✨
