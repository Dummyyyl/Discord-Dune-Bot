from random import choice, randint
from getprofitablewallet import generate_wallets_excel
from analyze import analyze_wallet

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, youre awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'wallets' in lowered:
        API_KEY = "pnd91Em3dsbdtx43Bdh1TuclsRa35AZv"
        QUERY_ID = 4694069
        OUTPUT_FILE = "wallets.xlsx"
        generate_wallets_excel(API_KEY, QUERY_ID, OUTPUT_FILE)
        return OUTPUT_FILE
    elif lowered.startswith('analyze '):
        wallet_address = lowered.split(' ')[1]
        return analyze_wallet(wallet_address)
    else:
        return None