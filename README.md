# Manhwa Downloader 📖

An automated, multi-threaded Python command-line utility to scrape, download, and compile manga/manhwa chapters into optimized PDF files.

## 🚀 Features

* **Multi-threaded Downloads:** Leverages `ThreadPoolExecutor` to speed up image downloads concurrently.
* **Automatic Compilation:** Downloads chapter images and compiles them directly into single-chapter PDF documents using `img2pdf`.
* **Chapter Merging:** Merges downloaded chapters across a specified range into a single combined PDF using `PyPDF2`.
* **Flexible Input:** Reads list of targets (name, range of chapters) from a YAML configuration file (`manhwa_list.yml`).
* **Session Cache:** Checks if files already exist to skip re-downloading.

## 📁 Repository Structure

* **`download_manhwa.py`**: The core execution script containing scraping, downloading, converting, and merging logic.
* **`manhwa_list.yml`**: Configuration file specifying the comics to download.
* **`requirements.txt`**: Standard Python package dependencies list.

## 🛠️ Setup and Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DileepKumarD/DownloadManhwa.git
   cd DownloadManhwa
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your download list:**
   Edit `manhwa_list.yml` to specify which manhwa and chapters you want to download. The format is a comma-separated and space-separated list of items:
   ```yaml
   manhwa-slug,start-chapter,end-chapter,download-name
   ```

4. **Run the script:**
   ```bash
   python download_manhwa.py
   ```
