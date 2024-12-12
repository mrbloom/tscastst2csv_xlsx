import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings

def parse_tscast_html(html_content):
    """
    Parse the TSCast HTML and extract stream information into a pandas DataFrame.
    
    Parameters:
    html_content (str): HTML content of the page
    
    Returns:
    pandas.DataFrame: Structured data of TSCast streams
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
        
        # Extract input bitrate (updated to use string instead of text)
        bitrate_elems = item.find_all('div', class_='not-initialized')
        bitrate = next((elem.get_text(strip=True) for elem in bitrate_elems if 'Mbit' in elem.get_text()), 'Unknown Bitrate')
        
        # Extract programs
        programs_elem = item.find('div', class_='ts-cast-program-streams')
        program_name = programs_elem.get_text(strip=True) if programs_elem else 'No Program'
        
        # Extract sinks
        sinks = []
        sink_names = []
        sink_details = []
        sink_bitrates = []
        
        sink_elems = item.find_all('div', class_='in-out txt-center')
        for sink in sink_elems:
            # Sink name (like "KATV Азербайджан")
            sink_name_elem = sink.find_all('div', class_='not-initialized')
            sink_name = sink_name_elem[1].get_text(strip=True) if len(sink_name_elem) > 1 else 'Unknown Sink'
            
            # Sink details
            sink_details_text = sink.get('title', 'No sink details')
            
            # Sink bitrate
            sink_bitrate_elem = sink.find_all('div', class_='not-initialized')
            sink_bitrate = sink_bitrate_elem[-1].get_text(strip=True) if sink_bitrate_elem else 'Unknown Bitrate'
            
            sinks.append({
                'name': sink_name,
                'details': sink_details_text,
                'bitrate': sink_bitrate
            })
            
            # Separate lists for easier DataFrame creation
            sink_names.append(sink_name)
            sink_details.append(sink_details_text)
            sink_bitrates.append(sink_bitrate)
        
        # Compile stream information
        stream_info = {
            'Source': source_name,
            'Input Details': input_details,
            'Input Bitrate': bitrate,
            'Program': program_name,
            'Sink Names': ', '.join(sink_names),
            'Sink Details': ', '.join(sink_details),
            'Sink Bitrates': ', '.join(sink_bitrates),
            'Full Sinks Info': str(sinks)
        }
        
        stream_data.append(stream_info)
    
    # Create DataFrame
    df = pd.DataFrame(stream_data)
    
    return df

def main():
    try:
        # Read the HTML file
        with open('10.101.130.22.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Parse the HTML
        result_df = parse_tscast_html(html_content)

        # Display the DataFrame
        print(result_df)

        # Optionally, save to CSV
        result_df.to_csv('tscast_streams.csv', index=False)
        print("\nData has been saved to tscast_streams.csv")

    except FileNotFoundError:
        print("Error: paste.txt file not found. Please ensure the file exists in the same directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
