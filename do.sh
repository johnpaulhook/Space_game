#!/bin/bash
MODULE=spacegame
# Function to display usage
show_usage() {
    echo "Usage: $0 [conda|help]"
    echo "  conda    - Build the spacegame conda enviornment"
    echo "  help     - Show this help message"
    echo ""
    echo ""
    echo "Example: $0 conda"
    echo "Example: $0 help"
}

build_conda() {
    which conda
    conda --version
    echo "---------------------------------------------------------------------"
    conda config --set always_yes true
    conda deactivate || true
    conda remove --name "${MODULE}" --all || true
    conda env create -f ./environment.yml || conda env update --prune -f ./environment.yml
    echo "---------------------------------------------------------------------"
    conda info --envs
    conda list
    echo "===================================================================="
    echo "Please run now first:   conda activate ${MODULE}"
}

# Handle command line arguments
if [ $# -ge 1 ]; then
    choice=$1
    
    # Check if help is requested
    if [ "$choice" = "help" ] || [ "$choice" = "-h" ] || [ "$choice" = "--help" ]; then
        show_usage
        exit 0
    fi

    if [ "$choice" = "conda" ]; then
        build_conda
        exit 0
    fi
    
    # Setup environment
    setup_environment
else
    show_usage
    exit 1
fi