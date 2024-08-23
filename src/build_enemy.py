"""
A script permitting to read `data/enemy.csv` and write content into a `.py` file (containg a dict definition).

This procedure permits to avoid using pandas (heavy lib) during the main.

Usage: On a terminal:
```
python build_enemy.py
```
"""
import pandas as pd
from numpy import nan
from os.path import dirname, abspath, join

# 0/ PATHS
# ------------------------------------------------------
# ENV PATH
SRC_PATH = dirname(abspath(__file__))
# <absolute_path>/android/src/
ROOT_PATH = dirname(SRC_PATH)
# <absolute_path>/android/
# Path where file is read
output_file_path = "enemy.py"
# Path to the CSV to read
OPPONENT_DATA_PATH = join(ROOT_PATH, "data", "enemy.csv")

# 2/ Open CSV > into dict
# ------------------------------------------------------
df = pd.read_csv(OPPONENT_DATA_PATH, sep=";")

# Set the index column
df.set_index("Name", inplace=True)

# Convert the DataFrame to a nested dictionary
nested_dict = df.replace([nan], [None], regex=False).to_dict(orient='index')

# 3/ dict into .py file
# ------------------------------------------------------
def write_dict_to_py(dictionary: dict, file_path: str, dict_name: str='opponent_datasheets') -> None:
    """
    Wirte dict `dictionnary` into a .py file containing :
    ```
    <dict_name> = ... < content of the dict>
    ```
    """
    def format_value(value):
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, dict):
            return format_dict(value)
        else:
            return str(value)

    def format_dict(d, indent=0):
        items = []
        for key, value in d.items():
            formatted_value = format_value(value)
            items.append(f"{'    ' * (indent + 1)}'{key}': {formatted_value}")
        return '{\n' + ',\n'.join(items) + f"\n{'    ' * indent}}}"

    with open(file_path, 'w') as file:
        file.write(f"{dict_name} = {format_dict(dictionary)}\n")


if __name__ == "__main__":
    # Launch
    write_dict_to_py(nested_dict, output_file_path)
    print(f"Successfuly transformed '{OPPONENT_DATA_PATH}' into '{output_file_path}'")
