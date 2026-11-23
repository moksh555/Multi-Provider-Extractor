PDF_EXTRACTION_PROMPT = """You extract one invoice PDF into the structured schema provided with this request. Fill only that schema. Do not add fields, omit fields, or wrap the result in markdown.

Read only what is printed. Do not invent values. Keep text as printed. Dates are YYYY-MM-DD. Money and rates are plain numbers: no currency symbol and no thousands separator. A printed 7.5% is 0.075. Only these fields may be null when they are not printed: due_date, payment_terms, discount, tax_rate, tax, shipping, amount_paid, vendor_email, vendor_phone, po_number, and calculation_reason. A missing printed field is never "Pass": set calculation_status to "Human-Evaluation-Required" and name the missing field in calculation_reason.

After filling the printed values, recompute the invoice. For this check only, treat a missing discount, tax, shipping, or amount paid as 0. Do not overwrite a printed value with the recomputed one.

Check all of these:
- Each line amount equals quantity × unit price.
- Subtotal equals the sum of the line amounts.
- Tax equals (subtotal − discount) × tax rate. Skip this check when no tax rate is printed.
- Total equals subtotal − discount + tax + shipping.
- Balance due equals total − amount paid.

Allow a difference of 0.02 for rounding. Set calculation_status to "Pass" only when every printed field is present and every check holds. Set it to "Human-Evaluation-Required" when any printed figure disagrees, any field is missing, or a line cannot be checked. That missing-field case is never "Pass". On "Pass", leave calculation_reason null. On "Human-Evaluation-Required", name each missing field and each failed check with the printed value and the recomputed value.
"""
