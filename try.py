# d = {
#   "brand": "Ford",
#   "model": "Mustang",
#   "year": 1964
# }

# print(d["Mustang"])


# ### Error Handling 

# def set_age(age: int) -> None:
#     if age < 0:
#         raise ValueError("Age cannot be negative!")
#     print(f"Age set to {age}")

# try:
#     set_age(-5)
# except ValueError as error:
#     print(f"Caught error: {error}")
    
    
    
## pydantic Library 

from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
  id:int
  name: str
  email: EmailStr # validates actual email formatting 
  age: int = Field(ge=18) # Must be greater or equal to 18
  
# Valid data with string coercion (forcing the datatype to convert into another datatype)

user = User(
  id = "22", 
  name = 'Jews',
  email = "jews@israel.com",
  age = "54"
)
print(user.age) # converts into int
print(user.id) # converts into int


  
  
try:
    bad_user = User(id=1, name="Bob", email="not-an-email", age=15)
except :
    print("DataType Mismatch")