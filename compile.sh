#!/bin/bash

# LaTeX Compilation Script for MarketPulse Submission
echo "=========================================="
echo "  MarketPulse LaTeX Compilation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    print_error "pdflatex not found. Please install TeX Live."
    echo "Ubuntu/Debian: sudo apt-get install texlive-full"
    echo "macOS: brew install mactex"
    exit 1
fi

print_success "pdflatex found"

# Compile the report
echo ""
print_warning "Compiling report.tex..."
pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1
pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1  # Second pass for references
pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1  # Third pass for ToC

if [ -f "report.pdf" ]; then
    print_success "Report compiled successfully: report.pdf"
else
    print_error "Report compilation failed"
    echo "Run manually: pdflatex report.tex"
fi

# Compile the presentation
echo ""
print_warning "Compiling presentation.tex..."
pdflatex -interaction=nonstopmode presentation.tex > /dev/null 2>&1
pdflatex -interaction=nonstopmode presentation.tex > /dev/null 2>&1  # Second pass

if [ -f "presentation.pdf" ]; then
    print_success "Presentation compiled successfully: presentation.pdf"
else
    print_error "Presentation compilation failed"
    echo "Run manually: pdflatex presentation.tex"
fi

# Clean up auxiliary files
echo ""
print_warning "Cleaning up auxiliary files..."
rm -f *.aux *.log *.out *.toc *.lof *.lot *.nav *.snm *.vrb 2>/dev/null
print_success "Cleanup complete"

echo ""
echo "=========================================="
echo "  Compilation Complete!"
echo "=========================================="
echo ""
echo "Generated files:"
if [ -f "report.pdf" ]; then
    echo "  ✓ report.pdf ($(du -h report.pdf | cut -f1))"
fi
if [ -f "presentation.pdf" ]; then
    echo "  ✓ presentation.pdf ($(du -h presentation.pdf | cut -f1))"
fi
echo ""
echo "To open PDFs:"
echo "  xdg-open report.pdf"
echo "  xdg-open presentation.pdf"
echo ""
