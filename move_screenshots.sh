#!/bin/bash
# Move all .png files from Desktop to Documents/Screenshots
# Creates the destination folder if it doesn't exist

SRC="/Users/anlindeb/Desktop"
DST="/Users/anlindeb/Documents/Screenshots"

mkdir -p "$DST"

count=0
for f in "$SRC"/*.png; do
    [ -e "$f" ] || continue  # skip if no .png files
    filename=$(basename "$f")
    
    # Handle duplicates — append number if file already exists
    if [ -e "$DST/$filename" ]; then
        name="${filename%.png}"
        i=1
        while [ -e "$DST/${name}_${i}.png" ]; do
            ((i++))
        done
        mv "$f" "$DST/${name}_${i}.png"
        echo "Moved: $filename → ${name}_${i}.png (duplicate)"
    else
        mv "$f" "$DST/$filename"
        echo "Moved: $filename"
    fi
    ((count++))
done

if [ $count -eq 0 ]; then
    echo "No .png files found on Desktop."
else
    echo "Done! Moved $count file(s) to $DST"
fi
