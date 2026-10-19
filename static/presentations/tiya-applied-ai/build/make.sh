#!/bin/sh
# Rebuild the whole course kit: decks, PowerPoint, documents, PDFs, index, zip.
set -eu
cd "$(dirname "$0")"
KIT=..
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

python3 make_decks.py
uv run --quiet --with python-pptx python make_pptx.py
python3 build.py > /dev/null

pdf() { # $1 = page in kit root, $2 = pdf name in downloads/
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
    --print-to-pdf="$PWD/$KIT/downloads/$2" "file://$(cd $KIT && pwd)/$1" 2>/dev/null
  echo "downloads/$2  $(du -h "$KIT/downloads/$2" | cut -f1)"
}
pdf day1-slides.html day1-slides.pdf
pdf day2-slides.html day2-slides.pdf
pdf tiya-ai-onsite.html program-agenda.pdf
pdf participant-workbook.html participant-workbook.pdf
pdf facilitator-guide.html facilitator-guide.pdf
pdf assessment-kit.html assessment-kit.pdf

zipkit() {
  (cd "$KIT" && rm -f downloads/tiya-ai-course-kit.zip && \
   zip -qr downloads/tiya-ai-course-kit.zip ./*.html downloads materials -x 'downloads/tiya-ai-course-kit.zip' -x '*.DS_Store')
}
zipkit
python3 build.py > /dev/null   # index now shows real sizes, including the zip
zipkit
echo "downloads/tiya-ai-course-kit.zip  $(du -h "$KIT/downloads/tiya-ai-course-kit.zip" | cut -f1)"
