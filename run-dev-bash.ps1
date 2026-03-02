# Run the reporter image with local app/templates/static mounted.
# Edit code on your machine, run this script to get HTML + PDF in ./output (no rebuild).
# Prereq: build once with:  docker build -t reporter .
# Bash version

# Create output directory if it doesn't exist
mkdir -p output

# Run the reporter image
docker run --rm `
  -v "$(pwd)/app:/app/app" `
  -v "$(pwd)/templates:/app/templates" `
  -v "$(pwd)/static:/app/static" `
  -v "$(pwd)/output:/output" `
  reporter `
  @args
