# LaTeX Academic Submission

This directory contains the LaTeX source files and compiled PDFs for the MarketPulse academic submission.

## 📄 Compiled Documents

| File | Size | Pages | Status | Description |
|------|------|-------|--------|-------------|
| **report.pdf** | 543KB | 44 | ✅ Ready | Complete academic report |
| **presentation.pdf** | 89KB | 36 | ✅ Ready | Beamer presentation slides |

## 📝 Source Files

- **report.tex** - Main report source (53KB)
- **presentation.tex** - Presentation source (30KB)
- **sections/** - Report chapters (introduction, architecture, etc.)
- **figures/** - Images and diagrams
- **compile.sh** - Compilation script

## 🔧 How to Compile

### Option 1: Using the Script (Recommended)

```bash
cd latex-submission/
./compile.sh
```

This will compile both the report and presentation.

### Option 2: Manual Compilation

**For the report:**
```bash
pdflatex report.tex
bibtex report
pdflatex report.tex
pdflatex report.tex
```

**For the presentation:**
```bash
pdflatex presentation.tex
pdflatex presentation.tex
```

## 📋 Document Structure

### Report (44 pages)

1. **Title Page** - Project title, authors, institution
2. **Abstract** - Executive summary
3. **Table of Contents** - Document navigation
4. **Chapter 1: Introduction** - Problem statement and motivation
5. **Chapter 2: Literature Review** - Related work
6. **Chapter 3: Architecture** - System design and Big Data pipeline
7. **Chapter 4: Data Collection** - Web scraping and data sources
8. **Chapter 5: Machine Learning** - Models, training, evaluation
9. **Chapter 6: Dashboard** - User interface and visualization
10. **Chapter 7: Results** - Performance metrics and evaluation
11. **Chapter 8: Conclusion** - Summary and future work
12. **References** - Bibliography
13. **Appendices** - Code listings, data sources, Morocco stocks

### Presentation (36 slides)

1. **Title Slide** - Project overview
2. **Problem Statement** - Morocco market challenges
3. **Architecture** - System design
4. **Big Data Pipeline** - Kafka, Spark, Cassandra
5. **Data Collection** - 10+ sources
6. **Machine Learning** - 5 models, 91% accuracy
7. **Dashboard Demo** - Live demonstration
8. **Results** - Performance metrics
9. **Impact** - Real-world value
10. **Future Work** - Roadmap
11. **Conclusion** - Summary
12. **Q&A** - Questions slide

## ✏️ Customization

Before submission, update these sections with your personal information:

### In report.tex (Lines 100-115)

```latex
\author{Your Name}
\studentid{Your Student ID}
\supervisor{Supervisor Name}
\university{Your University}
\department{Your Department}
\date{\today}
```

### In presentation.tex (Lines 35-37)

```latex
\author{Your Name}
\institute{Your University}
\date{\today}
```

## 🇫🇷 French Accents

All French accents have been properly encoded using LaTeX escape sequences:

- `é` → `\'e`
- `è` → `\`e`
- `ô` → `\^o`
- `à` → `\`a`

Examples:
- Médias24 → `M\'edias24`
- L'Économiste → `L'\'Economiste`
- Crédit → `Cr\'edit`
- Hôtelier → `H\^otelier`

## 📊 Key Statistics Included

- **91% prediction accuracy** (directional)
- **<500ms latency** (p99)
- **1,000+ events/second** throughput
- **60+ Morocco stocks** covered
- **10+ data sources** aggregated
- **40+ features** engineered
- **15,000+ lines** of code

## 🔍 Document Features

### Report Features

- Professional two-column IEEE format
- Syntax-highlighted code listings
- Architecture diagrams
- Performance graphs
- Complete bibliography
- Morocco stock market data appendix
- Data sources documentation
- Prediction features appendix

### Presentation Features

- Professional Beamer theme
- Consistent color scheme
- Code snippets with syntax highlighting
- Architecture diagrams
- Performance metrics
- Live demo slides
- Q&A preparation slide

## 📦 Files Included

```
latex-submission/
├── README.md                    ← This file
├── compile.sh                   ← Compilation script
├── report.tex                   ← Report source (53KB)
├── report.pdf                   ← Report PDF (543KB, 44 pages) ✅
├── report.lof                   ← List of figures
├── report.lot                   ← List of tables
├── presentation.tex             ← Presentation source (30KB)
├── presentation.pdf             ← Presentation PDF (89KB, 36 slides) ✅
├── presentation.nav             ← Beamer navigation
├── presentation.snm             ← Beamer snippets
├── sections/                    ← Report chapters
│   ├── introduction.tex
│   ├── literature.tex
│   ├── architecture.tex
│   ├── data_collection.tex
│   ├── machine_learning.tex
│   ├── dashboard.tex
│   ├── results.tex
│   └── conclusion.tex
└── figures/                     ← Images and diagrams
    └── (architecture diagrams, screenshots, etc.)
```

## ✅ Pre-Submission Checklist

- [ ] Personal information updated in report.tex
- [ ] Personal information updated in presentation.tex
- [ ] Both PDFs compiled successfully
- [ ] Report is 44 pages (543KB)
- [ ] Presentation is 36 slides (89KB)
- [ ] All figures displaying correctly
- [ ] Code listings formatted properly
- [ ] French accents rendering correctly
- [ ] Bibliography complete
- [ ] Appendices included

## 🎓 For Academic Submission

**What to submit:**

1. **report.pdf** - Main academic report (44 pages)
2. **presentation.pdf** - Presentation slides (36 slides)
3. **Source files** (optional) - All .tex files and dependencies
4. **GitHub repository URL** - Link to code repository

**Recommended submission format:**

```
MarketPulse_Submission/
├── MarketPulse_Report.pdf        ← report.pdf (renamed)
├── MarketPulse_Presentation.pdf  ← presentation.pdf (renamed)
├── MarketPulse_SourceCode/       ← GitHub repository (optional)
└── README.txt                    ← Submission notes
```

## 📞 Troubleshooting

### Missing Packages

If compilation fails due to missing packages:

```bash
sudo apt-get install texlive-full  # Ubuntu/Debian
```

Or install specific packages:
```bash
sudo apt-get install texlive-latex-extra texlive-fonts-recommended
```

### Encoding Errors

If you see UTF-8 encoding errors, verify French accents are escaped:
- Check that all `é`, `è`, `ô` characters use LaTeX escapes
- Example: `Médias24` should be `M\'edias24`

### Compilation Errors

If LaTeX won't compile:

1. Check the .log file for specific errors
2. Ensure all `\begin{}` have matching `\end{}`
3. Verify all file paths are correct
4. Check that `lstlisting` environments are in `[fragile]` frames

---

**Status:** ✅ Both documents compiled successfully and ready for submission

**Last Updated:** January 4, 2026
