# Photos and Video Sorter  ୧⍤⃝📷 ⟶ 🗃️

## Overview 
A python script to organize photos and videos into separate folders, sorted by years and months based on their creation date. 

## Features 
* retrieve date either from filename starting by YYYY-MM-DD or by using EXIF metadata
* Sort photos into separate directories organized by year and month
* Sort files that do not have date in a separate folder (to_sort)
* Avoid overwritting existing files
* Display a short summary of the sorting operation 

## Installation
### Create a virtual env
First create and activate a virtual environments using the corresponding command 
* using [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) 
```bash
    conda create -n <env_name> python=3.12
    conda activate <env_name>
```
* using linux / MacOS
```bash
    python -m venv .venv
    source .venv/bin/activate
```
* using windows(CMD)
```bash
    python -m venv .venv
    .venv\Scripts\activate
```
### Install requirements
```bash
    pip install -r requirements.txt
```

## Usage 
1. Configure paths in config.py 
    * ORIGIN: source folder containing photos and videos to sort 
    * PHOTOS_DESTINATION and VIDEOS_DESTINATION: destination folders for sorted files 
    * Set MANUAL_SELECTION = True to select folders via pop-up windows instead.
    * INITIALDIR: dir from which the pop-up windows start

2. Run the script: 
```sh
    python sort_photos_and_videos.py 
```

## Troubleshooting 
Feel free to reach out if you come across any bug or have suggestions for new feature ! 