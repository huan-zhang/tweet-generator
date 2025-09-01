"""
Crypto price prediction module for generating engaging cryptocurrency predictions.
Picks trending coins and generates predictions with AI-generated reasoning.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from config import Config

logger = logging.getLogger(__name__)


class CryptoPredictor:
    """Generates crypto price predictions for social media posts."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Popular crypto coins to predict (symbol: name)
        self.crypto_coins = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum', 
            'BNB': 'Binance Coin',
            'XRP': 'Ripple',
            'ADA': 'Cardano',
            'DOGE': 'Dogecoin',
            'MATIC': 'Polygon',
            'SOL': 'Solana',
            'DOT': 'Polkadot',
            'SHIB': 'Shiba Inu',
            'AVAX': 'Avalanche',
            'LINK': 'Chainlink',
            'UNI': 'Uniswap',
            'LTC': 'Litecoin',
            'ATOM': 'Cosmos'
        }
        
        # Fallback predictions if API fails
        self.fallback_predictions = [
            "🚀 Bitcoin could see a 15% surge next week as institutional adoption accelerates! The recent regulatory clarity might push BTC to new monthly highs. #Bitcoin #BTC #CryptoNews",
            "📈 Ethereum looking bullish for next week! Smart contract upgrades and DeFi growth could drive ETH up 20%. Watch for the breakout above key resistance! #Ethereum #ETH #DeFi",
            "⚡ Solana showing strong technical patterns! Could pump 25% next week with increased NFT activity and ecosystem growth. Don't sleep on SOL! #Solana #SOL #NFTs",
            "🔥 Cardano (ADA) setup looks promising for next week. Ecosystem developments and partnerships could trigger a 18% rally. Perfect accumulation zone! #Cardano #ADA #Crypto",
            "💎 Polygon (MATIC) ready to explode! Layer 2 adoption growing rapidly. Predicting 22% gains next week as more projects migrate. #Polygon #MATIC #Layer2"
        ]
    
    def generate_prediction(self) -> str:
        """Generate a crypto prediction post."""
        try:
            # Try to get real market data first
            coin_data = self._get_trending_coin()
            
            if coin_data:
                return self._create_prediction_with_data(coin_data)
            else:
                # Fallback to manual prediction
                return self._create_manual_prediction()
                
        except Exception as e:
            logger.error(f"Error generating crypto prediction: {str(e)}")
            return random.choice(self.fallback_predictions)
    
    def _get_trending_coin(self) -> Optional[Dict]:
        """Get trending coin data from CoinGecko API (free tier)."""
        try:
            # CoinGecko free API - get trending coins
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Pick a random trending coin
                if data.get('coins') and len(data['coins']) > 0:
                    trending_coin = random.choice(data['coins'][:7])  # Top 7 trending
                    coin_info = trending_coin.get('item', {})
                    
                    # Get more details about this coin
                    coin_id = coin_info.get('id')
                    if coin_id:
                        return self._get_coin_details(coin_id)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching trending coins: {str(e)}")
            return None
    
    def _get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """Get detailed coin information."""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.warning(f"Error fetching coin details for {coin_id}: {str(e)}")
            return None
    
    def _create_prediction_with_data(self, coin_data: Dict) -> str:
        """Create prediction using real coin data."""
        try:
            name = coin_data.get('name', 'Unknown')
            symbol = coin_data.get('symbol', '').upper()
            
            # Get current price
            current_price = None
            market_data = coin_data.get('market_data', {})
            if market_data:
                price_usd = market_data.get('current_price', {}).get('usd')
                if price_usd:
                    current_price = float(price_usd)
            
            # Generate prediction percentage (5% to 35%)
            prediction_percent = random.randint(5, 35)
            
            # Generate reasoning
            reasons = [
                "strong technical breakout pattern forming",
                "increased whale accumulation detected",
                "major partnership announcements expected", 
                "ecosystem development accelerating",
                "regulatory clarity improving sentiment",
                "institutional adoption growing",
                "network upgrade coming soon",
                "DeFi integration expanding",
                "NFT marketplace integration planned",
                "cross-chain compatibility improving"
            ]
            
            reason = random.choice(reasons)
            
            # Create prediction text
            if current_price and current_price > 0.01:
                price_str = f"${current_price:.2f}" if current_price < 100 else f"${current_price:,.0f}"
            else:
                price_str = ""
            
            prediction_text = f"🚀 {name} ({symbol}) looking bullish for next week! "
            
            if price_str:
                prediction_text += f"Currently at {price_str}, "
            
            prediction_text += f"predicting {prediction_percent}% gains as {reason}. "
            prediction_text += f"Perfect entry opportunity! #{symbol} #Crypto #Prediction"
            
            # Ensure it's not too long
            if len(prediction_text) > 270:
                prediction_text = f"🚀 {name} ({symbol}) could pump {prediction_percent}% next week! {reason.capitalize()}. #{symbol} #Crypto #Prediction"
            
            logger.info(f"Generated prediction for {name} ({symbol}): {prediction_percent}% gain")
            return prediction_text
            
        except Exception as e:
            logger.error(f"Error creating prediction with data: {str(e)}")
            return self._create_manual_prediction()
    
    def _create_manual_prediction(self) -> str:
        """Create prediction using manual coin list."""
        try:
            # Pick random coin from our list
            symbol = random.choice(list(self.crypto_coins.keys()))
            name = self.crypto_coins[symbol]
            
            # Generate prediction percentage (8% to 30%)
            prediction_percent = random.randint(8, 30)
            
            # Generate reasoning
            reasons = [
                "technical analysis shows bullish patterns",
                "whale accumulation increasing",
                "ecosystem growth accelerating", 
                "partnership rumors circulating",
                "network upgrades approaching",
                "institutional interest growing",
                "DeFi adoption expanding",
                "market sentiment turning positive",
                "key resistance levels breaking",
                "trading volume surging"
            ]
            
            reason = random.choice(reasons)
            
            # Emojis for different coins
            coin_emojis = {
                'BTC': '₿', 'ETH': '⟐', 'BNB': '🟡', 'XRP': '💧', 'ADA': '🔷',
                'DOGE': '🐕', 'MATIC': '🟣', 'SOL': '☀️', 'DOT': '⭕', 'SHIB': '🚀',
                'AVAX': '🏔️', 'LINK': '🔗', 'UNI': '🦄', 'LTC': '🥈', 'ATOM': '⚛️'
            }
            
            emoji = coin_emojis.get(symbol, '🚀')
            
            prediction_text = f"{emoji} {name} ({symbol}) prediction: {prediction_percent}% pump next week! "
            prediction_text += f"{reason.capitalize()}. Great accumulation opportunity! "
            prediction_text += f"#{symbol} #Crypto #Prediction"
            
            logger.info(f"Generated manual prediction for {name} ({symbol}): {prediction_percent}% gain")
            return prediction_text
            
        except Exception as e:
            logger.error(f"Error creating manual prediction: {str(e)}")
            return random.choice(self.fallback_predictions)
    
    def generate_batch_predictions(self, count: int = 1) -> List[str]:
        """Generate multiple predictions."""
        predictions = []
        
        for i in range(count):
            try:
                prediction = self.generate_prediction()
                predictions.append(prediction)
                logger.info(f"Generated crypto prediction {i+1}/{count}")
            except Exception as e:
                logger.error(f"Error generating prediction {i+1}: {str(e)}")
                predictions.append(random.choice(self.fallback_predictions))
        
        return predictions


# Test function
if __name__ == "__main__":
    from config import Config
    
    config = Config()
    predictor = CryptoPredictor(config)
    
    print("Testing crypto prediction generation:")
    for i in range(3):
        prediction = predictor.generate_prediction()
        print(f"\nPrediction {i+1}: {prediction}")
        print(f"Length: {len(prediction)} characters")