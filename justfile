# Generate talk slideshows and landing page
generate:
    dev/bin/python generate_talks.py talks/ html/

# Force regenerate all talks
force:
    dev/bin/python generate_talks.py talks/ html/ --force

# Clean output directory
clean:
    rm -rf html/
