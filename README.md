# Direct_Skip
Converts LightBox Data to Direct Skip

# Property CSV Mapper

A Streamlit web application that maps property search CSV files to a standardized format based on predefined column mappings.

## Features

- **CSV File Upload**: Easy drag-and-drop CSV file upload
- **Column Mapping**: Automatically maps input columns to standardized output columns
- **Custom Fields**: Adds a custom "Property Reference Code" field to all records
- **Data Validation**: Validates input files and provides helpful error messages
- **Preview Functionality**: Shows preview of both input and output data
- **Download Export**: Generates and downloads the mapped CSV file
- **Clean Interface**: User-friendly Streamlit interface with progress indicators

## Column Mapping

The application maps the following columns from your property search CSV:

| Input Column | Output Column |
|-------------|---------------|
| OWNER_1_FIRST | Last Name |
| OWNER_1_LAST | First Name |
| OWNER_ADDRESS | Mailing Address |
| OWNER_CITY | Mailing City |
| OWNER_STATE | Mailing State |
| OWNER_ZIP | Mailing Zip |
| PROP_ADDRESS | Property Address |
| PROP_CITY | Property City |
| PROP_STATE | Property State |
| PROP_ZIP | Property Zip |

Additionally, a "Custom Field 1" column is added with your specified Property Reference Code.

## Installation

### Local Development

1. Clone this repository:
```bash
git clone <your-repo-url>
cd property-csv-mapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy the app by selecting `app.py` as your main file

## Usage

1. **Upload CSV File**: Click the file uploader and select your property search CSV file
2. **Enter Reference Code**: Provide a Property Reference Code that will be added to all records
3. **Preview Data**: Review the input data and mapping results
4. **Download**: Click the download button to get your mapped CSV file

## File Structure

```
property-csv-mapper/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## Requirements

- Python 3.8 or higher
- Streamlit 1.28.0 or higher
- Pandas 2.0.0 or higher

## Input File Format

Your input CSV should contain columns matching the expected property search format. The application will validate that required columns are present and provide warnings for missing columns.

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Missing required columns
- Corrupted CSV files
- Processing errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please create an issue in the GitHub repository.
