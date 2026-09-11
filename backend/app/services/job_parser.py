from app.schemas.job_parser import JobParseRequest,JobParseResponse
import re
class JobParserService:

    @staticmethod
    async def parse(text: str, url:str | None = None) -> JobParseResponse:
        if not url:
            match = re.search(r'https?://[^\s<>"]+', text)
            if match:
                url = match.group(0)

        text_lower = text.lower()
        if (
            "remote" in text_lower
            or "wfh" in text_lower
            or "work from home" in text_lower
            ):
            location_type = "remote"
        elif "hybrid" in text_lower:
            location_type = 'hybrid'
        elif ("onsite" in text_lower 
            or "on-site" in text_lower
            or "in-office" in text_lower):
            location_type = 'onsite'
        else:
            location_type = None



        def parse_amount(val_str: str) -> int:
                    cleaned = val_str.lower().replace("₹", "").replace("$", "").replace(",", "").strip()
                    if cleaned.endswith("k"):
                        return int(float(cleaned[:-1]) * 1000)
                    if cleaned.endswith("l"):
                        return int(float(cleaned[:-1]) * 100000)
                    return int(float(cleaned))
        
        pattern = (
            r"[\$₹]?(\d[\d,]*(?:[kl])?)\s*(?:-|to)\s*[\$₹]?(\d[\d,]*(?:[kl])?)"
        )


        sal_match = re.search(pattern, text, re.IGNORECASE)
        salary_min, salary_max = None, None
        if sal_match:
            salary_min = parse_amount(sal_match.group(1))
            salary_max = parse_amount(sal_match.group(2))

        company_name, role_title = None, None

        hiring_match = re.search(
        r"([A-Za-z0-9\s&-]+?)\s+is hiring\s+(?:a|an)?\s*([A-Za-z0-9\s/&-]+?)(?=[.,\n(]|$)",
        text,
        re.IGNORECASE,
        )
        if hiring_match:
            company_name = hiring_match.group(1).strip()
            role_title = hiring_match.group(2).strip()
        else:

            at_match = re.search(
            r"([A-Za-z0-9\s/&-]+?)\s+(?:at|@)\s+([A-Za-z0-9\s&-]+?)(?=[.,\n(]|$)",
            text,
            re.IGNORECASE,
        )
            if at_match:
                role_title = at_match.group(1).strip()
                company_name = at_match.group(2).strip()

        if company_name:
            company_name = (
            company_name.split(".")[0].split("(")[0].split("\n")[0].strip()
            )

        if role_title:
            role_title = role_title.split(".")[0].split("(")[0].split("\n")[0].strip()

        return JobParseResponse(
        company_name=company_name,
        role_title=role_title,
        location_type=location_type,
        salary_range_min=salary_min,
        salary_range_max=salary_max,
        job_url=url,
        raw_posting_text=text,
        )