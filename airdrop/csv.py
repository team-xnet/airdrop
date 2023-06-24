"""CSV generation related methods."""
from csv     import DictWriter
from pathlib import Path

def generate_csv(data: list[dict], path: str):
	"""Generates and writes given `data` dictionary into `path`.

	Args:
		data (dict): CSV data itself. The dictionary structure must be as follows: Address: str, SOLO: int, XRP: int, Ratio: int, Split: str
		path (str): Output path for the CSV file. Must also include the
	"""
	if not path.endswith(".csv"):
		path = path + ".csv"
	with open(Path(path).resolve(), "w", encoding="UTF8", newline="") as file:
		# Rendered CSV column headers. Must also be the same as the dictionary keys!
		columns = ["Address", "SOLO", "XRP", "Ratio", "Split"]
		writer = DictWriter(file, fieldnames=columns)
		writer.writeheader()
		writer.writerows(data)
