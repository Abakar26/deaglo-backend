from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User


class CustomToken(RefreshToken):
    """
    Custom token class that includes user role as a claim.
    """

    @classmethod
    def for_user(cls, user: User):
        # Call the superclass method to get a RefreshToken instance
        token = super().for_user(user)

        # Add custom claims. For instance, add the user's role.
        token["level"] = user.type_user_role.name.upper().replace(" ", "_")
        return token


def generate_tokens_manually(user: User):
    """
    Generate refresh and access tokens manually for a given user.

    Parameters:
        user (User): The user for whom tokens are generated.

    Returns:
        dict: A dictionary containing the refresh and access tokens.

    Example:
        To manually generate tokens for a user, call this function with the user instance:

        user = User.objects.get(username='example_user')
        tokens = generate_tokens_manually(user)
        # Output: {'refresh': '...', 'access': '...'}
    """

    tokens = CustomToken.for_user(user)
    return {
        "refresh": str(tokens),
        "access": str(tokens.access_token),
    }
