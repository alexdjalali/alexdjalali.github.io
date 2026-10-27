#!/bin/sh
# Rebuild the whole course kit: decks, PowerPoint, Day 3 files, agendas, pages, PDFs, index, zips.
set -eu
cd "$(dirname "$0")"
KIT=..
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DAYS="day1 day2 day3"

python3 make_decks.py
uv run --quiet --with python-pptx python make_pptx.py
uv run --quiet --with markdown python make_sops.py
uv run --quiet --with openpyxl python make_day3.py
python3 make_agendas.py
python3 make_pages.py
python3 build.py > /dev/null

pdf() { # $1 = page in kit root, $2 = pdf name in downloads/
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
    --print-to-pdf="$PWD/$KIT/downloads/$2" "file://$(cd $KIT && pwd)/$1" 2>/dev/null
  echo "downloads/$2  $(du -h "$KIT/downloads/$2" | cut -f1)"
}
for d in $DAYS; do
  pdf "$d-slides.html" "$d-slides.pdf"
  pdf "agenda-$d.html" "agenda-$d.pdf"
  pdf "participant-workbook-$d.html" "participant-workbook-$d.pdf"
  pdf "assessment-kit-$d.html" "assessment-kit-$d.pdf"
done
pdf facilitator-guide.html facilitator-guide.pdf
pdf day2-outline.html day2-outline.pdf
pdf day3-outline.html day3-outline.pdf
# Approval packet: the two outlines back to back, each still its own document.
uv run --quiet --with pypdf python -c "
from pypdf import PdfWriter
w = PdfWriter()
for f in ('day2-outline', 'day3-outline'):
    w.append('$KIT/downloads/' + f + '.pdf')
w.write('$KIT/downloads/day2-day3-outlines-for-approval.pdf')
"
echo "downloads/day2-day3-outlines-for-approval.pdf  $(du -h "$KIT/downloads/day2-day3-outlines-for-approval.pdf" | cut -f1)"

python3 make_zips.py
python3 build.py > /dev/null   # pages now show real sizes, including the zips
python3 make_zips.py           # re-zip so the zipped pages show those sizes too
