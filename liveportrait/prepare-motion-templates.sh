#!/bin/bash
# Prepare motion templates for idle animations
# This script helps you create reusable motion templates from driving videos

set -e

echo "🎬 LivePortrait Motion Template Preparation"
echo "=========================================="
echo ""

# Check if shared directory exists
SHARED_DIR="./shared/liveportrait_motions"
mkdir -p "$SHARED_DIR"

echo "📁 Motion templates will be stored in: $SHARED_DIR"
echo ""

# Function to download example driving videos
download_examples() {
    echo "📥 Downloading example driving videos..."
    echo ""
    
    # Create examples directory
    mkdir -p "$SHARED_DIR/examples"
    
    # Note: These are placeholder URLs - you'll need to provide actual driving videos
    echo "ℹ️  To create motion templates, you need driving videos showing:"
    echo "   - Blinking"
    echo "   - Breathing (subtle chest/shoulder movement)"
    echo "   - Head nodding"
    echo "   - Combined idle movements"
    echo ""
    echo "📝 You can:"
    echo "   1. Record yourself performing these motions"
    echo "   2. Use existing videos from LivePortrait examples"
    echo "   3. Download from the LivePortrait repository"
    echo ""
    echo "💡 Tips for recording driving videos:"
    echo "   - Use 1:1 aspect ratio (square video)"
    echo "   - 512x512 or 256x256 resolution"
    echo "   - 2-5 seconds duration"
    echo "   - Front-facing, well-lit"
    echo "   - Neutral expression at start and end (for looping)"
    echo "   - Focus on one motion type per video"
    echo ""
}

# Function to create a motion template
create_template() {
    local video_file="$1"
    local template_name="$2"
    local description="$3"
    
    if [ ! -f "$video_file" ]; then
        echo "❌ Video file not found: $video_file"
        return 1
    fi
    
    echo "🎬 Creating template: $template_name"
    echo "   Description: $description"
    echo "   Source: $video_file"
    
    # Copy to shared directory with standardized name
    cp "$video_file" "$SHARED_DIR/${template_name}.mp4"
    
    # Create metadata file
    cat > "$SHARED_DIR/${template_name}.json" <<EOF
{
  "name": "$template_name",
  "description": "$description",
  "source_file": "$(basename "$video_file")",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "recommended_multiplier": 0.8,
  "loop_friendly": true,
  "duration_seconds": $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_file" 2>/dev/null || echo "unknown")
}
EOF
    
    echo "✅ Template created: $SHARED_DIR/${template_name}.mp4"
    echo ""
}

# Function to optimize video for motion template
optimize_video() {
    local input_file="$1"
    local output_file="$2"
    
    echo "🔧 Optimizing video for motion template..."
    
    # Check if ffmpeg is available
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  ffmpeg not found. Skipping optimization."
        echo "   Install ffmpeg for video optimization features."
        cp "$input_file" "$output_file"
        return
    fi
    
    # Optimize: resize to 512x512, 30fps, good quality
    ffmpeg -i "$input_file" \
        -vf "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2" \
        -r 30 \
        -c:v libx264 \
        -preset medium \
        -crf 23 \
        -y \
        "$output_file" 2>/dev/null
    
    echo "✅ Video optimized: $output_file"
}

# Function to create seamless loop
create_seamless_loop() {
    local input_file="$1"
    local output_file="$2"
    
    echo "🔄 Creating seamless loop..."
    
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  ffmpeg not found. Skipping loop creation."
        return 1
    fi
    
    # Create a seamless loop by reversing the last second
    ffmpeg -i "$input_file" \
        -filter_complex "[0:v]split[v0][v1];[v0]trim=0:4[v0t];[v1]trim=4:5,reverse[v1r];[v0t][v1r]concat=n=2:v=1[outv]" \
        -map "[outv]" \
        -c:v libx264 \
        -preset medium \
        -crf 23 \
        -y \
        "$output_file" 2>/dev/null
    
    echo "✅ Seamless loop created: $output_file"
}

# Main menu
echo "What would you like to do?"
echo ""
echo "1. Download example driving videos (info only)"
echo "2. Create motion template from video file"
echo "3. Optimize video for motion template"
echo "4. Create seamless loop from video"
echo "5. List existing templates"
echo "6. Create standard template set (requires videos)"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        download_examples
        ;;
    
    2)
        read -p "Enter path to driving video: " video_path
        read -p "Enter template name (e.g., 'blink', 'breathing'): " template_name
        read -p "Enter description: " description
        
        if [ -f "$video_path" ]; then
            create_template "$video_path" "$template_name" "$description"
        else
            echo "❌ File not found: $video_path"
        fi
        ;;
    
    3)
        read -p "Enter path to video file: " video_path
        read -p "Enter output filename: " output_name
        
        if [ -f "$video_path" ]; then
            optimize_video "$video_path" "$SHARED_DIR/$output_name"
        else
            echo "❌ File not found: $video_path"
        fi
        ;;
    
    4)
        read -p "Enter path to video file: " video_path
        read -p "Enter output filename: " output_name
        
        if [ -f "$video_path" ]; then
            create_seamless_loop "$video_path" "$SHARED_DIR/$output_name"
        else
            echo "❌ File not found: $video_path"
        fi
        ;;
    
    5)
        echo "📋 Existing motion templates:"
        echo ""
        if [ -d "$SHARED_DIR" ] && [ "$(ls -A $SHARED_DIR/*.mp4 2>/dev/null)" ]; then
            for template in "$SHARED_DIR"/*.mp4; do
                template_name=$(basename "$template" .mp4)
                if [ -f "$SHARED_DIR/${template_name}.json" ]; then
                    echo "📹 $template_name"
                    cat "$SHARED_DIR/${template_name}.json" | grep -E "(description|duration|recommended_multiplier)" | sed 's/^/   /'
                    echo ""
                else
                    echo "📹 $template_name (no metadata)"
                    echo ""
                fi
            done
        else
            echo "   No templates found in $SHARED_DIR"
        fi
        ;;
    
    6)
        echo "📦 Creating standard template set..."
        echo ""
        echo "This requires you to provide driving videos for:"
        echo "  - blink.mp4 (blinking motion)"
        echo "  - breathing.mp4 (breathing motion)"
        echo "  - head_nod.mp4 (head nodding motion)"
        echo "  - idle_combined.mp4 (combined idle motions)"
        echo ""
        echo "Place these files in the current directory and run this option again."
        echo ""
        
        # Check for standard templates
        templates_found=0
        
        if [ -f "blink.mp4" ]; then
            create_template "blink.mp4" "blink" "Natural eye blinking animation"
            ((templates_found++))
        fi
        
        if [ -f "breathing.mp4" ]; then
            create_template "breathing.mp4" "breathing" "Subtle breathing motion"
            ((templates_found++))
        fi
        
        if [ -f "head_nod.mp4" ]; then
            create_template "head_nod.mp4" "head_nod" "Gentle head nodding"
            ((templates_found++))
        fi
        
        if [ -f "idle_combined.mp4" ]; then
            create_template "idle_combined.mp4" "idle_combined" "Combined idle motions (blink + breathing + subtle movement)"
            ((templates_found++))
        fi
        
        if [ $templates_found -eq 0 ]; then
            echo "⚠️  No standard template videos found."
            echo ""
            echo "💡 To create templates, you can:"
            echo "   1. Record yourself performing each motion"
            echo "   2. Use examples from LivePortrait repository"
            echo "   3. Extract from existing videos"
        else
            echo "✅ Created $templates_found template(s)"
        fi
        ;;
    
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ Done!"
echo ""
echo "📁 Templates location: $SHARED_DIR"
echo "💡 Use these templates with create-idle-animation.py"
echo ""
