# replace_pixabay_page_url.py
"""
Replace ONLY the Pixabay page URL with the direct image URL.
Targets: https://pixabay.com/illustrations/island-hot-air-ballon-birds-sunset-8465139/
"""

import re
from pathlib import Path

# The URL to replace (Pixabay page URL)
OLD_URL = "https://pixabay.com/illustrations/island-hot-air-ballon-birds-sunset-8465139/"

# The correct direct image URL
NEW_URL = "https://cdn.pixabay.com/photo/2023/12/23/08/42/island-8465139_1280.png"

def replace_in_file(filepath, dry_run=False):
    """Replace the specific Pixabay page URL with the direct image URL."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file contains the old URL
    if OLD_URL not in content:
        return False, 0
    
    # Count how many times it appears
    count = content.count(OLD_URL)
    
    # Replace ALL occurrences
    new_content = content.replace(OLD_URL, NEW_URL)
    
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return True, count

def find_files_with_url(base_dir):
    """Find all HTML files containing the Pixabay page URL."""
    files_with_url = []
    
    for html_file in base_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if OLD_URL in content:
                files_with_url.append(html_file)
        except:
            pass
    
    return files_with_url

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--file', help='Process a specific file')
    parser.add_argument('--dir', help='Process a specific directory')
    parser.add_argument('--verbose', action='store_true', help='Show more details')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🔄 REPLACING PIXABAY PAGE URL WITH DIRECT IMAGE URL")
    print("=" * 80)
    print(f"📌 Old URL: {OLD_URL}")
    print(f"📌 New URL: {NEW_URL}")
    print(f"🧪 Dry run: {'ON' if args.dry_run else 'OFF'}")
    print("=" * 80 + "\n")
    
    if args.file:
        # Process a single file
        filepath = Path(args.file)
        if filepath.exists():
            print(f"📄 Processing: {filepath}")
            modified, count = replace_in_file(filepath, args.dry_run)
            if modified:
                if args.dry_run:
                    print(f"  📝 Would replace {count} occurrences")
                else:
                    print(f"  ✅ Modified ({count} occurrences replaced)")
            else:
                print("  ⏭️ URL not found in this file")
        else:
            print(f"❌ File not found: {filepath}")
        return
    
    if args.dir:
        # Process a specific directory
        dir_path = Path(args.dir)
        if dir_path.exists():
            search_dir = dir_path
        else:
            print(f"❌ Directory not found: {dir_path}")
            return
    else:
        # Search from current directory
        search_dir = Path('.')
    
    print(f"🔍 Searching in: {search_dir}/")
    
    # Find all files with the URL
    files_with_url = find_files_with_url(search_dir)
    
    if not files_with_url:
        print("\n❌ No files found containing the Pixabay page URL!")
        return
    
    print(f"\n📊 Found {len(files_with_url)} files containing the URL\n")
    
    total_modified = 0
    total_replaced = 0
    
    for filepath in sorted(files_with_url):
        # Show relative path
        try:
            rel_path = filepath.relative_to(search_dir)
        except:
            rel_path = filepath
        
        print(f"📄 {rel_path}")
        
        modified, count = replace_in_file(filepath, args.dry_run)
        
        if modified:
            total_modified += 1
            total_replaced += count
            if args.dry_run:
                print(f"  📝 Would replace {count} occurrences")
            else:
                print(f"  ✅ MODIFIED ({count} occurrences replaced)")
        else:
            print(f"  ⏭️ No changes needed")
    
    print("\n" + "=" * 80)
    print(f"📊 FINAL SUMMARY:")
    print(f"  📄 Files containing the URL: {len(files_with_url)}")
    print(f"  ✏️ Files modified: {total_modified}")
    print(f"  🔄 Occurrences replaced: {total_replaced}")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes.")
    else:
        print("\n✅ Done! All Pixabay page URLs replaced with direct image URLs.")

if __name__ == "__main__":
    main()