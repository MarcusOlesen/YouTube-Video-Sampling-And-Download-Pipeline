
# Youtube-Download-DATALAB

This repository provides a reproducible pipeline for downloading and organizing YouTube videos from participants in the [Nordic YouTube Data Donation Project](https://norden.diva-portal.org/smash/record.jsf?pid=diva2%3A1954799&dswid=9605). The project investigates how digital platforms influence public discourse and develops ethical, legally compliant methods for collecting and processing user-contributed data.

The pipeline uses [yt-dlp](https://github.com/yt-dlp/yt-dlp), an actively maintained open-source tool for downloading YouTube content and metadata.


## What the Pipeline Does

The *Youtube-Download-DATALAB* workflow is designed to:

* **Ingest** watch history JSON files from participants.
* **Clean and standardize** the metadata into a consistent dataset.
* **Sample and download** YouTube videos and related information for research.
* **Organize outputs** for downstream analysis in a transparent and reproducible way.

This work forms part of [DATALAB](https://datalab.au.dk/)'s mission to advance democratic, ethical, and human-centered digital research.
For a detailed discussion of the dataset and research framework, see:
[Data donation as a method for investigating trends and challenges in digital media landscapes at national scale (PDF)](https://norden.diva-portal.org/smash/get/diva2:1954799/FULLTEXT01.pdf).


## Repository Structure

| File / Notebook                 | Description                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| `Pre_Download.ipynb`            | Preprocessing: import watch history JSON files, clean metadata, and prepare manifest files. |
| `Video_Download_Pipeline.ipynb` | Main pipeline: sample, download, and organize videos using `yt-dlp`.                        |
| `download_utils.py`             | Reusable helper functions for downloading and organizing videos.                            |
| `environment.yml`               | Conda environment specification for reproducibility.                                        |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MarcusOlesen/Youtube-Download-DATALAB.git
cd Youtube-Download-DATALAB
```

### 2. Set up the environment

Using **conda**:

```bash
conda env create -f environment.yml
conda activate datalab-env
```

### 3. Run the pipeline

The workflow is notebook-based:

1. Start with **`Pre_Download.ipynb`** to prepare and clean the watch history dataset.
2. Move on to **`Video_Download_Pipeline.ipynb`** to sample and download the videos.

You can also import the helper functions directly into your own Python workflow:

```python
from download_utils import download_video

video_url = "https://www.youtube.com/watch?v=example"
download_video(video_url, output_dir="downloads/")
```

# AU-DATALAB

DATALAB – Center for Digital Social Research is an interdisciplinary research center at the School of Communication and Culture. The center is based on the vision that technology and data systems should maintain a focus on people and society, supporting the principles of democracy, human rights and ethics.


All research and activities of the center is focusing on three contemporary challenges facing the digital society, that is the challenge of 1) preserving conditions for privacy, autonomy and trust among individuals and groups; 2) sustaining the provision of and access to high-quality content online to safeguard democracy; and 3) maintaining a suitable and meaningful balance between algorithmic and human control in connection with automation.

<p align="center">
  <img width="460" src="https://github.com/AU-DATALAB/AU-DATALAB/blob/main/images/Datalab_logo_blue_transparent.png">
</p>

For more information, visit [DATALAB's website](https://datalab.au.dk/).
