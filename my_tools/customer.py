import importlib

from agents import function_tool

from models.company import CompanyData
from utils.md_loader import load_markdown


@function_tool
def getCompanyData(company_id: str) -> CompanyData:
    """
    Get company information about the company using its id and return name and context. If user ask question about any company use this to get company information.
    """
    print(f"Getting info about {company_id}")
    data = load_markdown(f"customers/{company_id}/data.md")
    module = importlib.import_module(f"customers.{company_id}.about")
    about = module.name
    return CompanyData(name=about, context=data)
