from app.models.user import User
from app.models.customer import Customer, CustomerFamily, CustomerEmployment, CustomerBanking, CustomerExistingProduct
from app.models.product import HDFCProduct
from app.models.recommendation import Recommendation

__all__ = [
    "User",
    "Customer",
    "CustomerFamily",
    "CustomerEmployment",
    "CustomerBanking",
    "CustomerExistingProduct",
    "HDFCProduct",
    "Recommendation",
]
