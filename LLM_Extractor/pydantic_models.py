from pydantic import BaseModel, Field

class Items(BaseModel):
    description: str = Field(..., description="The description of the item")
    quantity: float = Field(..., description="The quantity of the item")
    unit_price: float = Field(..., description="The unit price of the item")
    amount: float = Field(..., description="The amount of the item")

class ExtractionRequest(BaseModel):
    invoice_id: str = Field(..., description="The id of the invoice same as invoice_number")
    invoice_number: str = Field(..., description="The number of the invoice")
    company_name: str = Field(..., description="The name of the company the bill is sent from")
    company_address: str = Field(..., description="The address of the company the bill is sent from")
    customer_name: str = Field(..., description="The name of the customer the bill is sent to")
    billing_address: str = Field(..., description="The address of the customer the bill is sent to")
    invoice_date: str = Field(..., description="The date of the invoice")
    due_date: str | None = Field(None, description="The due date of the invoice")
    currency: str = Field(..., description="The currency of the invoice")
    payment_terms: str | None = Field(None, description="The payment terms of the invoice")
    status: str = Field(..., description="The status of the invoice")
    items: list[Items] = Field(..., description="The items of the invoice")
    subtotal: float = Field(..., description="The subtotal of the invoice")
    discount: float | None = Field(None, description="The discount of the invoice")
    tax_rate: float | None = Field(None, description="The tax rate of the invoice")
    tax: float | None = Field(None, description="The tax of the invoice")
    shipping: float | None = Field(None, description="The shipping of the invoice")
    total: float = Field(..., description="The total of the invoice")
    amount_paid: float | None = Field(None, description="The amount paid of the invoice")
    balance_due: float = Field(..., description="The balance due of the invoice")
    vendor_email: str | None = Field(None, description="The email of the vendor")
    vendor_phone: str | None = Field(None, description="The phone number of the vendor")
    po_number: str | None = Field(None, description="The purchase order number of the invoice")
    calculation_status: str = Field(..., description="Pass only when every field is present and every check holds. Human-Evaluation-Required when any field is missing or any check fails.")
    calculation_reason: str | None = Field(None, description="Null on Pass. On Human-Evaluation-Required, names each missing field and each failed check.")

class PricingResponse(BaseModel):
    Input_tokens: float = Field(..., description="The input tokens of the pricing")
    Output_tokens: float = Field(..., description="The output tokens of the pricing")
    Cache_write_tokens: float | None = Field(..., description="The cache write tokens of the pricing")
    Cache_read_tokens: float | None = Field(..., description="The cache read tokens of the pricing")
    Total_price: float = Field(..., description="The total price of the pricing")

class ExtractionsResponse(BaseModel):
    ExtractionRequests: list[ExtractionRequest]
    Input_tokens: int = Field(..., description="The input tokens of the extraction")
    Output_tokens: int = Field(..., description="The output tokens of the extraction")
    Output_thinking_tokens: int = Field(..., description="The output thinking tokens of the extraction")
    model: str = Field(..., description="The model used for the extraction")
    Pricing: PricingResponse = Field(..., description="The pricing of the extraction")

