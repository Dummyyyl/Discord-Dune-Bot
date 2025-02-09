import csv
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
import time

ua = UserAgent(os='linux', browsers=['firefox'])

class BulkWalletChecker:

    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
        self.shorten = lambda s: f"{s[:4]}...{s[-5:]}" if len(s) >= 9 else s
        self.skippedWallets = 0
        self.proxyPosition = 0
        self.results = []

    def randomise(self):
        self.identifier = random.choice([browser for browser in tls_client.settings.ClientIdentifiers.__args__ if browser.startswith(('chrome', 'safari', 'firefox', 'opera'))])
        self.sendRequest = tls_client.Session(random_tls_extension_order=True, client_identifier=self.identifier)
        self.sendRequest.timeout_seconds = 60

        parts = self.identifier.split('_')
        identifier, version, *rest = parts
        other = rest[0] if rest else None
        
        os = 'windows'
        if identifier == 'opera':
            identifier = 'chrome'
        elif version == 'ios':
            os = 'ios'
        else:
            os = 'windows'

        self.user_agent = UserAgent(browsers=[identifier], os=[os]).random

        self.headers = {
            'Host': 'gmgn.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.user_agent
        }

    def getTokenDistro(self, wallet: str):
        url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/{wallet}/unique_token_7d?interval=30d"
        retries = 3
        tokenDistro = []

        for attempt in range(retries):
            self.randomise()
            try:
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True).json()
                tokenDistro = response['data']['tokens']
                if tokenDistro:  
                    break
            except Exception:
                time.sleep(1)
            
            try:
                response = self.cloudScraper.get(url, headers=self.headers, allow_redirects=True).json()
                tokenDistro = response['data']['tokens']
                if tokenDistro:
                    break
            except Exception:
                time.sleep(1)
        
        if not tokenDistro:
            return {
                "No Token Distribution Data": None
            }

        FiftyPercentOrMore = 0
        ZeroToFifty = 0
        FiftyTo100 = 0
        TwoToFour = 0
        FiveToSix = 0
        SixPlus = 0
        NegativeToFifty = 0 

        for profit in tokenDistro:
            total_profit_pnl = profit.get('total_profit_pnl')
            if total_profit_pnl is not None:
                profitMultiplier = total_profit_pnl * 100

                if profitMultiplier <= -50:
                    FiftyPercentOrMore += 1
                elif -50 < profitMultiplier < 0:
                    NegativeToFifty += 1
                elif 0 <= profitMultiplier < 50:
                    ZeroToFifty += 1
                elif 50 <= profitMultiplier < 199:
                    FiftyTo100 += 1
                elif 200 <= profitMultiplier < 499:
                    TwoToFour += 1
                elif 500 <= profitMultiplier < 600:
                    FiveToSix += 1
                elif profitMultiplier >= 600:
                    SixPlus += 1

        return {
            "-50% +": FiftyPercentOrMore,
            "0% - -50%": NegativeToFifty,
            "0 - 50%": ZeroToFifty,
            "50% - 199%": FiftyTo100,
            "200% - 499%": TwoToFour,
            "500% - 600%": FiveToSix,
            "600% +": SixPlus
        }

    def getWalletData(self, wallet: str):
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=7d"
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']
                        return self.processWalletData(wallet, data, self.headers)
            
            except Exception as e:
                print(f"[🐲] Error fetching data, trying backup...")
            
            try:
                self.randomise()
                response = self.cloudScraper.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        data = data['data']
                        return self.processWalletData(wallet, data, self.headers)
            
            except Exception as e:
                print(f"[🐲] Backup scraper failed, retrying...")
            
            time.sleep(1)
        
        print(f"[🐲] Failed to fetch data for wallet {wallet} after {retries} attempts.")
        return None

    
    def processWalletData(self, wallet, data, headers):
        direct_link = f"https://gmgn.ai/sol/address/{wallet}"
        
        # Fix SOL Balance Handling
        sol_balance = "?"
        if 'sol_balance' in data and data['sol_balance'] is not None:
            try:
                # Remove potential commas and convert to float
                balance_value = float(str(data['sol_balance']).replace(',', ''))
                sol_balance = f"{balance_value:.2f} SOL"
            except ValueError:
                sol_balance = "Invalid balance format"

        # Winrate Handling
        winrate_7d = f"{data['winrate'] * 100:.2f}%" if data.get('winrate') is not None else "?"
        winrate_30d = self.get_30d_winrate(wallet)

        tokenDistro = self.getTokenDistro(wallet)
        tags = data.get('tags', "?")

        return {
            "wallet": wallet,
            "totalProfitPercent": f"{data['total_profit_pnl'] * 100:.2f}%" if data.get('total_profit_pnl') is not None else "error",
            "7dUSDProfit": f"${data['realized_profit_7d']:,.2f}" if data.get('realized_profit_7d') is not None else "error",
            "30dUSDProfit": f"${data['realized_profit_30d']:,.2f}" if data.get('realized_profit_30d') is not None else "error",
            "winrate_7d": winrate_7d,
            "winrate_30d": winrate_30d,
            "tags": tags,
            "sol_balance": sol_balance,
            "token_distribution": tokenDistro if tokenDistro else {},
            "directLink": direct_link,
            "buy_7d": str(data.get('buy_7d', "?"))
        }

    def get_30d_winrate(self, wallet):
        """Helper function to retrieve 30-day winrate"""
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d"
        try:
            # First attempt with TLS client
            response = self.sendRequest.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                if data.get('winrate') is not None:
                    return f"{data['winrate'] * 100:.2f}%"
        except Exception as e:
            print(f"[🐲] Primary 30d winrate fetch failed: {str(e)}")

        try:
            # Fallback to cloudscraper
            response = self.cloudScraper.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                if data.get('winrate') is not None:
                    return f"{data['winrate'] * 100:.2f}%"
        except Exception as e:
            print(f"[🐲] Backup 30d winrate fetch failed: {str(e)}")

        return "?"

def analyze_wallet(wallet: str) -> str:
    checker = BulkWalletChecker()
    result = checker.getWalletData(wallet)
    if result:
        output = f"**Wallet Analysis for {wallet}:**\n\n"
        output += f"**Total Profit Percentage:** {result['totalProfitPercent']}\n"
        output += f"**7-Day USD Profit:** {result['7dUSDProfit']}\n"
        output += f"**30-Day USD Profit:** {result['30dUSDProfit']}\n"
        output += f"**7-Day Winrate:** {result['winrate_7d']}\n"
        output += f"**30-Day Winrate:** {result['winrate_30d']}\n"
        output += f"**SOL Balance:** {result['sol_balance']}\n"
        output += f"**Buy 7-Day:** {result['buy_7d']}\n"
        output += f"**Tags:** {result['tags']}\n"
        
        output += "\n**Token Distribution:**\n"
        for category, value in result['token_distribution'].items():
            output += f"- {category}: {value}\n"
        
        output += f"\n**Direct Link:** [Click Here]({result['directLink']})\n"
        return output
    else:
        return f"Failed to analyze wallet {wallet}."