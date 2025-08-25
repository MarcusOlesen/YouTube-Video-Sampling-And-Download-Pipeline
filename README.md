# Youtube-Download-DATALAB

This repository provides a pipeline for downloading YouTube videos from participants who have donated their data as part of the **[Nordic YouTube Data Donation Project](https://norden.diva-portal.org/smash/get/diva2:1954799/FULLTEXT01.pdf)**. The project explores how digital platforms shape public discourse, and how user-contributed data can be collected and processed for research under strict ethical and legal safeguards.  

The repository leverages [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), a robust open-source command-line tool for downloading videos and associated metadata from YouTube.  

---

## About the Project

The **Youtube-Download-DATALAB** pipeline is designed to:
- Retrieve YouTube videos and metadata from participants in the donated dataset.  
- Standardize and organize the downloaded media for downstream research.  
- Ensure reproducibility, transparency, and alignment with research ethics.  

This work is part of DATALAB’s broader mission to support **democratic, ethical, and human-centered digital research**. For details on the underlying dataset and research framework, see the official project report:  
📄 [Data Donation Initiative: Nordic YouTube Data Donation Project (PDF)](https://norden.diva-portal.org/smash/get/diva2:1954799/FULLTEXT01.pdf)  

---

## Usage

The pipeline builds directly on [`yt-dlp`](https://github.com/yt-dlp/yt-dlp). Please refer to its documentation for installation, advanced options, and troubleshooting.  

Example usage within this project may look like:  

```bash
yt-dlp -o "%(uploader)s/%(title)s.%(ext)s" <video_url>
```

# AU-DATALAB

DATALAB – Center for Digital Social Research is an interdisciplinary research center at the School of Communication and Culture. The center is based on the vision that technology and data systems should maintain a focus on people and society, supporting the principles of democracy, human rights and ethics.


All research and activities of the center is focusing on three contemporary challenges facing the digital society, that is the challenge of 1) preserving conditions for privacy, autonomy and trust among individuals and groups; 2) sustaining the provision of and access to high-quality content online to safeguard democracy; and 3) maintaining a suitable and meaningful balance between algorithmic and human control in connection with automation.

<p align="center">
  <img width="460" src="https://github.com/AU-DATALAB/AU-DATALAB/blob/main/images/Datalab_logo_blue_transparent.png">
</p>

For more information, visit [DATALAB's website](https://datalab.au.dk/).
