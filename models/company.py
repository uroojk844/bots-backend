from pydantic import BaseModel


class CompanyData(BaseModel):
    name: str
    context: str
