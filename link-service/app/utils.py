import random
import string
import re

def generate_short_code(length=6):
    """
    Generate a random short code like 'aB3kR9'.
    
    We use:
    - lowercase letters: a-z
    - uppercase letters: A-Z  
    - digits: 0-9
    That's 62 possible characters.
    
    6 characters = 62^6 = 56 billion possible combinations.
    More than enough!
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid before we save it.
    We use a regex (regular expression) pattern.
    
    Valid examples:
      https://google.com
      http://example.org/path?query=1
    
    Invalid examples:
      just-some-text
      ftp://something  (we only allow http/https)
    """
    pattern = re.compile(
        r'^https?://'           # must start with http:// or https://
        r'(?:\S+(?::\S*)?@)?'   # optional user:password@
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)'  # domain
        r'+[A-Z]{2,6}'          # top level domain (.com, .org etc)
        r'(?::\d+)?'            # optional port number
        r'(?:/?|[/?]\S+)$',     # optional path
        re.IGNORECASE
    )
    return bool(pattern.match(url))

def sanitize_custom_slug(slug: str) -> str:
    """
    Clean up a user-provided custom slug.
    Only allow letters, numbers, and hyphens.
    
    Example: "My Cool Link!" -> "My-Cool-Link"
    """
    # Replace spaces with hyphens
    slug = slug.strip().replace(" ", "-")
    # Remove any character that is not a letter, number, or hyphen
    slug = re.sub(r"[^a-zA-Z0-9-]", "", slug)
    return slug[:30]  # max 30 characters