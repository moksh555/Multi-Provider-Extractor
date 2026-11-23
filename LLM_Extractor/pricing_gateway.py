from model_pricing import PRICING
from pydantic_models import PricingResponse

class PricingGateway:

    def get_pricing_claude_haiku(self, input_tokens: int, output_tokens: int, cache_write_tokens: int = 0, cache_read_tokens: int = 0):
        rates = PRICING["claude-haiku-5-5"]
        input_token_price = rates["input"] * input_tokens / 1_000_000
        output_token_price = rates["output"] * output_tokens / 1_000_000
        cache_write_price = rates["cache_write"] * cache_write_tokens / 1_000_000
        cache_read_price = rates["cache_read"] * cache_read_tokens / 1_000_000
        
        return PricingResponse(
            Input_tokens=input_token_price,
            Output_tokens=output_token_price,
            Cache_write_tokens=cache_write_price if cache_write_tokens > 0 else None,
            Cache_read_tokens=cache_read_price if cache_read_tokens > 0 else None,
            Total_price=input_token_price + output_token_price + cache_write_price + cache_read_price,
        )
    
    def get_pricing_gpt_luna(self, input_tokens: int, output_tokens: int, cache_write_tokens: int = 0, cache_read_tokens: int = 0):
        rates = PRICING["gpt-6-luna"]
        input_token_price = rates["input"] * input_tokens / 1_000_000
        output_token_price = rates["output"] * output_tokens / 1_000_000
        cache_write_price = rates["cache_write"] * cache_write_tokens / 1_000_000
        cache_read_price = rates["cache_read"] * cache_read_tokens / 1_000_000
        
        return PricingResponse(
            Input_tokens=input_token_price,
            Output_tokens=output_token_price,
            Cache_write_tokens=cache_write_price if cache_write_tokens > 0 else None,
            Cache_read_tokens=cache_read_price if cache_read_tokens > 0 else None,
            Total_price=input_token_price + output_token_price + cache_write_price + cache_read_price,
        )