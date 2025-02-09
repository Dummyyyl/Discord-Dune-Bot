import pandas as pd
from dune_client.client import DuneClient
from openpyxl import load_workbook

def generate_wallets_excel(api_key: str, query_id: int, output_file: str) -> None:
    # Initialize the DuneClient with your API key
    dune = DuneClient(api_key)

    # Fetch the latest result for the specified query ID
    query_result = dune.get_latest_result(query_id)

    # Extract trader (wallet) information from the result object
    trader_data = [row['trader'] for row in query_result.result.rows]

    # Convert the trader data into a pandas DataFrame
    df = pd.DataFrame(trader_data, columns=["Wallet Address"])

    # Write the DataFrame to an Excel file without the header
    df.to_excel(output_file, index=False, header=False)

    # Load the workbook and select the active worksheet
    wb = load_workbook(output_file)
    ws = wb.active

    # Autosize the column
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the column letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save the workbook
    wb.save(output_file)

    print(f"Wallet addresses saved to '{output_file}'")

# Example usage (can be removed or commented out if not needed)
if __name__ == "__main__":
    API_KEY = "pnd91Em3dsbdtx43Bdh1TuclsRa35AZv"
    QUERY_ID = 4694069
    OUTPUT_FILE = "wallets.xlsx"
    generate_wallets_excel(API_KEY, QUERY_ID, OUTPUT_FILE)
