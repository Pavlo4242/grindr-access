from grindr_user import GrindrUser
import os

def parse_grindr_info(filename="GrindrAccess_Info.txt"):
    """
    Parses the GrindrAccess_Info.txt file to extract credentials.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"'{filename}' not found. Please ensure it is in the same directory.")

    credentials = {}
    with open(filename, 'r') as f:
        for line in f:
            if ":" in line:
                key, value = line.split(":", 1)
                credentials[key.strip()] = value.strip()
    return credentials

def main():
    """
    Main function to run the automated Grindr session.
    """
    try:
        # 1. Parse credentials from the file
        print("Attempting to read credentials from GrindrAccess_Info.txt...")
        info = parse_grindr_info()
        
        # 2. Create a GrindrUser instance
        user = GrindrUser()

        # 3. Set the session using the credentials from the file
        user.set_session(
            profile_id=info.get("profileId"),
            auth_token=info.get("authToken"),
            l_device_info=info.get("l-device-info"),
            user_agent=info.get("user-agent")
        )
        print("Session information loaded successfully.")

        # 4. You can now use the API without logging in
        print("\n------------------- Fetching Profiles -------------------")
        # Example coordinates (center of the US)
        profiles = user.getProfiles(39.8283, -98.5795)
        print(profiles)

        print("\n------------------- Fetching Taps -------------------")
        taps = user.get_taps()
        print(taps)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
