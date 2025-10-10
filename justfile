# Generate talk slideshows and landing page
generate:
    dev/bin/python generate_talks.py talks/ html/
    open html/index.html

# Force regenerate all talks
force:
    dev/bin/python generate_talks.py talks/ html/ --force

# Clean output directory
clean:
    rm -rf html/

# Deploy to production server
deploy:
    rsync -avz --delete --exclude='.DS_Store' html/ vlaurent@ee-tik-vm047.ethz.ch:/local/home/web-talks-vanbever/public_html/
    ssh vlaurent@ee-tik-vm047.ethz.ch "sudo chown -R web-talks-vanbever:web-talks-vanbever /local/home/web-talks-vanbever/public_html/"
