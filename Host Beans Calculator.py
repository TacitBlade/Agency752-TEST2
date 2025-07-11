#!/usr/bin/env python3
"""
Beans to Diamonds Calculator
Convert your beans to diamonds with tier-based efficiency rates
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ConversionTier:
    """Represents a conversion tier with its properties"""
    min_beans: int
    max_beans: float
    diamonds_per_bean: float
    efficiency: float
    fixed_diamonds: Optional[int] = None

class BeansToDialmondsCalculator:
    """Calculator for converting beans to diamonds based on tier system"""
    
    def __init__(self):
        # Conversion tiers based on actual wallet data
        self.conversion_tiers = [
            ConversionTier(1, 8, 0.25, 25.00, 2),
            ConversionTier(9, 109, 0.2661, 26.61, 29),
            ConversionTier(110, 999, 0.2753, 27.53, 275),
            ConversionTier(1000, 3999, 0.2763, 27.63, 1105),
            ConversionTier(4000, 10999, 0.2768, 27.68, 3045),
            ConversionTier(11000, float('inf'), 0.2767, 27.67, None)
        ]
    
    def find_tier(self, beans: int) -> Optional[ConversionTier]:
        """Find the appropriate conversion tier for given beans amount"""
        for tier in self.conversion_tiers:
            if tier.min_beans <= beans <= tier.max_beans:
                return tier
        return None
    
    def calculate_diamonds(self, beans: int) -> Optional[Dict]:
        """Calculate diamonds from beans amount"""
        if not beans or beans <= 0:
            return None
        
        tier = self.find_tier(beans)
        if not tier:
            return None
        
        diamonds = 0
        remainder = 0
        
        # Use fixed diamond amounts for specific tiers when applicable
        if tier.fixed_diamonds and beans <= tier.max_beans:
            if beans == 8:
                diamonds = 2
            elif beans == 109:
                diamonds = 29
            elif beans == 999:
                diamonds = 275
            elif beans == 3999:
                diamonds = 1105
            elif beans == 10999:
                diamonds = 3045
            else:
                diamonds = math.floor(beans * tier.diamonds_per_bean)
                remainder = beans % math.ceil(1 / tier.diamonds_per_bean)
        else:
            diamonds = math.floor(beans * tier.diamonds_per_bean)
            remainder = beans % math.ceil(1 / tier.diamonds_per_bean)
        
        tier_number = self.conversion_tiers.index(tier) + 1
        
        return {
            'diamonds': diamonds,
            'remainder': remainder,
            'efficiency': tier.efficiency,
            'diamonds_per_bean': tier.diamonds_per_bean,
            'tier': tier_number
        }
    
    def display_tier_table(self):
        """Display the conversion tiers table"""
        print("\n" + "="*70)
        print("CONVERSION TIERS")
        print("="*70)
        print(f"{'Beans Range':<20} {'Rate':<12} {'Efficiency':<12} {'Example':<20}")
        print("-"*70)
        
        for i, tier in enumerate(self.conversion_tiers):
            max_beans_str = "∞" if tier.max_beans == float('inf') else f"{int(tier.max_beans):,}"
            beans_range = f"{tier.min_beans:,} - {max_beans_str}"
            rate = f"{tier.diamonds_per_bean:.4f}"
            efficiency = f"{tier.efficiency:.2f}%"
            
            if tier.fixed_diamonds and tier.max_beans < float('inf'):
                example = f"{int(tier.max_beans):,} beans = {tier.fixed_diamonds} diamonds"
            else:
                example = f"{tier.efficiency:.2f}% efficiency"
            
            print(f"{beans_range:<20} {rate:<12} {efficiency:<12} {example:<20}")
    
    def display_result(self, beans: int, result: Dict):
        """Display the conversion result"""
        print("\n" + "="*50)
        print("CONVERSION RESULT")
        print("="*50)
        print(f"Beans:           {beans:,}")
        print(f"Diamonds:        {result['diamonds']:,}")
        
        if result['remainder'] > 0:
            print(f"Beans Remainder: {result['remainder']}")
        
        print(f"Rate:            {result['diamonds_per_bean']:.4f} per bean")
        print(f"Efficiency:      {result['efficiency']:.2f}% (Tier {result['tier']})")
        print("="*50)
    
    def get_efficiency_tip(self, beans: int) -> str:
        """Get efficiency tip based on beans amount"""
        if beans < 109:
            return "💡 Tip: Efficiency increases significantly after 109 beans!"
        elif beans < 4000:
            return "💡 Tip: Maximum efficiency is reached at 4000+ beans!"
        else:
            return "💡 Great! You're at maximum efficiency tier!"
    
    def run_interactive(self):
        """Run the calculator in interactive mode"""
        print("🔥 BEANS TO DIAMONDS CALCULATOR 🔥")
        print("Convert your beans to diamonds with tier-based efficiency rates")
        
        while True:
            print("\nOptions:")
            print("1. Calculate conversion")
            print("2. View tier table")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                try:
                    beans_input = input("\nEnter number of beans: ").strip()
                    beans = int(beans_input)
                    
                    if beans <= 0:
                        print("❌ Please enter a positive number of beans!")
                        continue
                    
                    result = self.calculate_diamonds(beans)
                    if result:
                        self.display_result(beans, result)
                        print(f"\n{self.get_efficiency_tip(beans)}")
                    else:
                        print("❌ Unable to calculate conversion!")
                        
                except ValueError:
                    print("❌ Please enter a valid number!")
            
            elif choice == '2':
                self.display_tier_table()
            
            elif choice == '3':
                print("\n👋 Thanks for using the Beans to Diamonds Calculator!")
                break
            
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")

def main():
    """Main function to run the calculator"""
    calculator = BeansToDialmondsCalculator()
    
    # Check if running with command line arguments
    import sys
    if len(sys.argv) > 1:
        try:
            beans = int(sys.argv[1])
            result = calculator.calculate_diamonds(beans)
            if result:
                calculator.display_result(beans, result)
                print(f"\n{calculator.get_efficiency_tip(beans)}")
            else:
                print("❌ Unable to calculate conversion!")
        except ValueError:
            print("❌ Please provide a valid number of beans!")
            print("Usage: python beans_calculator.py <number_of_beans>")
    else:
        # Run in interactive mode
        calculator.run_interactive()

if __name__ == "__main__":
    main()
