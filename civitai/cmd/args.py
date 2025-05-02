import argparse

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Civitai files downloader")

parser.add_argument("out_dir", type=str, help="Output directory for downloaded files")

parser.add_argument(
    "--num_files",
    type=int,
    default=0,
    help="Number of files to download. If not specified, download all files.",
)

parser.add_argument(
    "--tags", nargs="+", type=int, default=[], help="Tags in numeric format"
)

parser.add_argument(
    "--max_workers", type=int, default=5, help="Max number of concurrent downloads"
)

args = parser.parse_args()
