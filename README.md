# Webcomic & Digital Comic Downloader & Compiler 📖

An automated, multi-threaded Python command-line utility designed to scrape, download, and compile webcomics and digital comic book chapters into organized PDF files.

## 🚀 Features

* **Multi-threaded Downloads:** Utilizes `ThreadPoolExecutor` to download asset images concurrently, optimizing network bandwidth.
* **Automatic PDF Compilation:** Compiles downloaded chapter images directly into single-chapter PDF documents using `img2pdf`.
* **Chapter Merging:** Merges multiple sequential chapter PDFs into a single combined volume using `PyPDF2`.
* **Flexible Batch Processing:** Reads targets (comic slug name, chapter range) from a YAML configuration file (`manhwa_list.yml`).
* **Caching Mechanism:** Proactively checks for existing files to prevent redundant downloads.

## 📁 Repository Structure

* **`download_manhwa.py`**: Core script containing web scraping, image downloading, and PDF compilation logic.
* **`manhwa_list.yml`**: Configuration file specifying download tasks.
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
   Edit `manhwa_list.yml` to specify targets. The format is a comma-separated and space-separated list of items:
   ```yaml
   comic-slug,start-chapter,end-chapter,download-name
   ```

4. **Run the compiler:**
   ```bash
   python download_manhwa.py
   ```
