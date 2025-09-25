from .generic_request import generic_post, generic_get, generic_put, generic_jpeg_upload

from .paths import (
    SESSIONS,
    TAP,
    GET_USERS,
    TAPS_RECIEVED,
    GET_PROFILE,
    STATUS,
    ALBUM,
    PROFILE,
    IMAGES,
    LOCATION
)
from .utils import to_geohash
import binascii
from functools import wraps


def check_banned(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.banned:
            return
        return func(self, *args, **kwargs)
    return wrapper


class GrindrUser:
    def __init__(self):
        self.banned = False

        self.sessionId = None
        self.profileId = ""
        self.authToken = None
        self.xmppToken = ""

        # Properties to hold info from the log file
        self.l_device_info = None
        self.user_agent = None

        self.proxy = None
        self.proxy_port = None

    def set_session(self, profile_id, auth_token, l_device_info, user_agent):
        """
        Manually sets the session information without logging in.
        """
        if not all([profile_id, auth_token, l_device_info, user_agent]):
            raise ValueError("Missing one or more required session parameters.")
            
        self.profileId = profile_id
        # The script uses sessionId and authToken interchangeably for the token.
        self.sessionId = auth_token 
        self.authToken = auth_token
        self.l_device_info = l_device_info
        self.user_agent = user_agent

    def set_proxy(self, proxy, proxy_port):
        self.proxy = proxy
        self.proxy_port = proxy_port

    def login(self, email, password):
        response = generic_post(
            SESSIONS,
            {"email": email, "password": password, "token": ""},
            proxy=self.proxy,
            proxy_port=self.proxy_port,
        )

        if "code" in response:
            code = response["code"]

            if code == 30:
                raise Exception("You need to verify your account via phone number!")

            if response["code"] == 27:
                self.banned = True
                raise Exception(f'Banned for {response["reason"]}')

            if response["code"] == 28:
                self.banned = True
                raise Exception("Banned")

            if response["code"] == 8:
                raise Exception("Deprecated client version")

        self.sessionId = response["sessionId"]
        self.profileId = response["profileId"]
        self.authToken = response["authToken"]
        self.xmppToken = response["xmppToken"]

    @check_banned
    def getProfiles(self, lat, lon):
        params = {
            "nearbyGeoHash": to_geohash(lat, lon),
            "onlineOnly": "false",
            "photoOnly": "false",
            "faceOnly": "false",
            "notRecentlyChatted": "false",
            "fresh": "false",
            "pageNumber": "1",
            "rightNow": "false",
        }

        response = generic_get(
            GET_USERS,
            params,
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    @check_banned
    def get_taps(self):
        response = generic_get(
            TAPS_RECIEVED,
            {},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    # type is a number from 1 - ?
    @check_banned
    def tap(self, profileId, type):
        response = generic_post(
            TAP,
            {"recipientId": profileId, "tapType": type},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    @check_banned
    def get_profile(self, profileId):
        response = generic_get(
            GET_PROFILE + profileId,
            {},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    # profileIdList MUST be an array of profile ids
    @check_banned
    def get_profile_statuses(self, profileIdList):
        response = generic_post(
            STATUS,
            {"profileIdList": profileIdList},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    @check_banned
    def get_album(self, profileId):
        response = generic_post(
            ALBUM,
            {"profileId": profileId},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    # returns session data (might renew it)
    @check_banned
    def sessions(self, email):
        response = generic_post(
            SESSIONS,
            {"email": email, "token": "", "authToken": self.authToken},
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )

        self.sessionId = response["sessionId"]
        self.profileId = response["profileId"]
        self.authToken = response["authToken"]
        self.xmppToken = response["xmppToken"]

        return response

    @check_banned
    def update_profile(self, data):
        response = generic_put(
            PROFILE,
            data,
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )
        return response

    # generating plain auth
    @check_banned
    def generate_plain_auth(self):
        auth = (
            self.profileId
            + "@chat.grindr.com"
            + "\00"
            + self.profileId
            + "\00"
            + self.xmppToken
        )
        _hex = binascii.b2a_base64(str.encode(auth), newline=False)
        _hex = str(_hex)
        _hex = _hex.replace("b'", "").replace("'", "")
        return _hex

    @check_banned
    def upload_image(self, file_io):
        return generic_jpeg_upload(
            "/v3/me/profile/images?thumbCoords=194%2C0%2C174%2C20",
            file_io,
            auth_token=self.sessionId,
            proxy=self.proxy,
            proxy_port=self.proxy_port,
            l_device_info=self.l_device_info,
            user_agent=self.user_agent
        )

    @check_banned
    def set_image(self, primary_hash, secondary_hashes=[]):
        data = {
            "primaryImageHash": primary_hash,
            "secondaryImageHashes": secondary_hashes,
        }

        return generic_put(IMAGES, data, auth_token=self.sessionId, proxy=self.proxy, proxy_port=self.proxy_port, l_device_info=self.l_device_info, user_agent=self.user_agent)

    @check_banned
    def set_location(self, lat, lng):
        data = {
            "geohash": to_geohash(lat, lng)
        }

        return generic_put(LOCATION, data, auth_token=self.sessionId, proxy=self.proxy, proxy_port=self.proxy_port, l_device_info=self.l_device_info, user_agent=self.user_agent)

