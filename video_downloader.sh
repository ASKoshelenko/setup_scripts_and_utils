#!/bin/bash

# Base URL
# Add your YOUR_URL like that "https://cdn.myownconference.net/4283/428395/1135/1135270/0bd45b4c382130f39cae0d1f0ec4ff8d"
base_url=YOUR_URL

# Define the quality pattern (720p in this case)
quality="720p"

# Starting and ending segment numbers (adjust as needed)
start=1
end=999

# Create a file list for ffmpeg
filelist="filelist.txt"
> "$filelist"

# Variable to track if any segments were found
found_any=false
consecutive_not_found=0
max_consecutive_not_found=10

for i in $(seq -f "%03g" $start $end); do
    filename="${quality}_${i}.ts"
    url="${base_url}/${filename}"

    echo "Checking URL: $url"
    
    # Check if the URL exists
    if curl --output /dev/null --silent --head --fail "$url"; then
        echo "Downloading $filename from $url"
        wget "$url" -O "$filename"
        if [ $? -eq 0 ]; then
            echo "file '$filename'" >> "$filelist"
            found_any=true
            consecutive_not_found=0
        else
            echo "Failed to download $filename"
        fi
    else
        echo "$filename does not exist. Continuing to next file."
        ((consecutive_not_found++))
    fi

    # Stop if 10 consecutive files are not found
    if [ $consecutive_not_found -ge $max_consecutive_not_found ]; then
        echo "No more segments found after $consecutive_not_found consecutive missing files."
        break
    fi
done

# Verify if any segments were found
if [ "$found_any" = false ]; then
    echo "Error: No segments were downloaded."
    exit 1
fi

# Combine segments into one video file
ffmpeg -f concat -i "$filelist" -c copy output.mp4

echo "Video has been created as output.mp4"

# Delete temporary .ts files
for file in *.ts; do
    rm -f "$file"
done

echo "Temporary files have been deleted."
