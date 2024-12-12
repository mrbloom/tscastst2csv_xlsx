from bs4 import BeautifulSoup
import pandas as pd
import warnings
from glob import glob
from pathlib import Path

def parse_tscast_html(html_content):
    """
    Parse the TSCast HTML and extract stream information, creating one row per sink.
    
    Parameters:
    html_content (str): HTML content of the page
    
    Returns:
    pandas.DataFrame: Structured data of TSCast streams with one row per sink
    """
    # Suppress specific deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tscast items
    tscast_items = soup.find_all('div', class_='tscast-item')
    
    # Prepare lists to store data
    stream_data = []
    
    for item in tscast_items:
        # Extract source name
        source_elem = item.find('div', class_='source')
        source_name = source_elem.get_text(strip=True) if source_elem else 'Unknown Source'
        
        # Extract input source details
        input_elem = item.find('div', class_='in-out')
        input_details = input_elem.get('title', 'No input details') if input_elem else 'No input details'
        
        # Extract input bitrate
        bitrate_elems = item.find_all('div', class_='not-initialized')
        input_bitrate = next((elem.get_text(strip=True) for elem in bitrate_elems if 'Mbit' in elem.get_text()), 'Unknown Bitrate')
        
        # Extract programs
        programs_elem = item.find('div', class_='ts-cast-program-streams')
        program_name = programs_elem.get_text(strip=True) if programs_elem else 'No Program'
        
        # Extract all sink names
        sink_elems = item.find_all('div', class_='in-out txt-center')
        sink_names = []
        sink_details = []
        sink_bitrates = []
        
        for sink in sink_elems:
            # Sink name (like "KATV Азербайджан")
            sink_name_elem = sink.find_all('div', class_='not-initialized')
            sink_name = sink_name_elem[1].get_text(strip=True) if len(sink_name_elem) > 1 else 'Unknown Sink'
            
            # Sink details
            sink_details_text = sink.get('title', 'No sink details')
            
            # Sink bitrate
            sink_bitrate_elem = sink.find_all('div', class_='not-initialized')
            sink_bitrate = sink_bitrate_elem[-1].get_text(strip=True) if sink_bitrate_elem else 'Unknown Bitrate'
            
            sink_names.append(sink_name)
            sink_details.append(sink_details_text)
            sink_bitrates.append(sink_bitrate)
        
        # Create a row for each sink
        for name, detail, bitrate in zip(sink_names, sink_details, sink_bitrates):
            stream_info = {
                'Source': source_name,
                'Input Details': input_details,
                'Input Bitrate': input_bitrate,
                'Program': program_name,
                'Sink Name': name,
                'Sink Bitrate': bitrate,
                'Sink Details': detail,
                
            }
            stream_data.append(stream_info)
    
    # Create DataFrame
    df = pd.DataFrame(stream_data)
    
    return df

def csv_to_xlsx(csv_file):
  """Converts a CSV file to an Excel file with the same filename.

  Args:
    csv_file: The path to the CSV file.
  """

  # Create Path objects for the CSV and Excel files
  csv_path = Path(csv_file)
  xlsx_path = csv_path.with_suffix('.xlsx')

  df = pd.read_csv(csv_path)
  df.to_excel(xlsx_path, index=False)

def make_csv_and_xlsx(html):
    try:
        # Read the HTML file
        with open(html, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse the HTML
        result_df = parse_tscast_html(html_content)

        # Display the DataFrame
        print(result_df)

        path = Path(html)
        filename_without_ext = path.stem
        csv_name = f"{filename_without_ext}.csv"
        result_df.to_csv(csv_name, index=False)
        csv_to_xlsx(csv_name)
        print("\nData has been saved")

    except FileNotFoundError:
        print("Error: paste.txt file not found. Please ensure the file exists in the same directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    for html in glob("*.html"):
        
        make_csv_and_xlsx(html)
        

if __name__ == "__main__":
    main()
