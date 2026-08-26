"Wattnet API"
import os
import requests
import datetime
from zoneinfo import ZoneInfo
from importlib.resources import files
from typing import ClassVar, Any

from typing_extensions import override

from .base import BaseProvider, provider, fetch_url
from ..version import user_agent
from ..exceptions import ProviderAuthenticationError, InvalidLocationError
from ..forecast import PointEstimate, Timeseries

# Generated from WattNet API zones get request piped into jq | grep "zones"
# and cleaned up.
WATTNET_ZONES: set[str] = set(
    (files("cats") / "data" / "wattnet_zones.txt").read_text().split()
)

@provider("wattnet.eu")
class WattnetEuProvider(BaseProvider):
    """
    Experimental provider for the wattnet.eu project API

    This can be used by passing the --api='wattnet.eu' command line
    argument. The service covers most of Europe with the location specified
    using a short code that typically refers to a single country. Data has 
    15 minute resolution and extends 4 days into the future.  
    
    Note that this provider is an experimental service and requires authentication.
    You will need to arrange a user name and password to be set outside of CATS
    and specify these in two environment variables: CATS_WATTNET_EMAIL and
    CATS_WATTNET_PASSWORD. CATS arranges to use these to obtain a short term
    access token.
    """
    BASE_URL: ClassVar[str] = "https://api.wattnet.eu"

    def update_authorization_token(self) -> None:
        """
        Update the short-lived access token for the wattnet API
        
        To access the watnet API an access token is needed. This can
        be obtained using an API call with a pre-authorized email address
        and password. The access token is stored in the api_key attribute.
        This method gets a new token (with a the email address and password
        extracted from environment variables) and updates the api_key attribute.
        
        NB: the HTTP calls in this method are not cached.
        """
        email = os.environ.get('CATS_WATTNET_EMAIL')
        password = os.environ.get('CATS_WATTNET_PASSWORD')
        if (email is None) or (password is None):
            raise ProviderAuthenticationError(
                            "CATS_WATTNET_EMAIL and CATS_WATTNET_PASSWORD "
                            "environment variables must be set for the wattnet provider"
                        )
        data = {"email": email, "password": password}
        headers = {"Content-Type": "application/json"}
        headers.update(user_agent)
        url = f"{self.base_url}/token-request/get_token"
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise ProviderAuthenticationError(
                f"WattNet token request failed with status {response.status_code}"
            )
        result = response.json()
        self.api_key = result["access_token"]
        self.token_expires = datetime.datetime.fromisoformat(result["expires_at"])

    @override
    def get_max_duration_minutes(self, metric: str | None = None) -> int:
        return 5745 # Looks like 4 days of data, lop off 15 mins from the end

    @override
    def get_temporal_resolution_minutes(self, metric: str | None = None) -> int:
        return 15 # Looks like 15 min resolution 

    @override
    def get_data(
        self,
        timestamp: datetime.datetime,
        location: str | None = None,
        metric: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Timeseries:
        location = self.validate_location(location)
        # Sort out the start time for caching
        if timestamp.minute > 45:
            patch_minute = 46
        elif timestamp.minute > 30:
            patch_minute = 31 
        elif timestamp.minute > 15:
            patch_minute = 16 
        else:
            patch_minute = 1
        start_time = timestamp.replace(minute=patch_minute, second=0,
                                       microsecond=0)
        end_time = start_time + datetime.timedelta(
            minutes=self.get_max_duration_minutes())
        
        # Build URL. Note that because we use timezone aware datetime object
        # (and force them into UTC) .isoformat() adds +00:00 to the end of 
        # the times in the URL. This breaks things. Instead we use strftime 
        # and check that the timezone offset is 0 as needed
        assert start_time.utcoffset() == datetime.timedelta(0), "Internal timezone error"
        url = (
            f"{self.base_url}/v1/footprints?"
            "footprint_type=carbon&"
            f"zone={location}&"
            f"start={start_time.strftime('%Y-%m-%dT%H:%M:%S')}&"
            f"end={end_time.strftime('%Y-%m-%dT%H:%M:%S')}"
        )
        self.update_authorization_token()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response: list | None = fetch_url(url, headers=headers)

        # Invalid responses may return empty lists. We've done the useful
        # validation already, so just raise an assertion error.
        assert response is not None, "No response from Wattnet request" # To catch failed for typing
        assert response, "Empty response from Wattnet request" # empty list is Falsey 

        # The "Z" at the end of the format string indicates UTC,
        # however, strptime does not know how to parse this, so we
        # need to add tzinfo data. Extract data and create a Timeserise
        # of data
        datefmt = "%Y-%m-%dT%H:%M:%SZ"
        utc = ZoneInfo("UTC")
        values = [
            PointEstimate(
                datetime=datetime.datetime.strptime(
                    d[0], datefmt).replace(tzinfo=utc),
                value=d[1],
            )
            for d in response[0]['series'][0]['values']
        ]
        return Timeseries("Carbon intensity", values=values, unit="gCO2eq/kWh")
        

    @override
    def validate_location(self, location: str | None) -> str:
        if location is None:
            raise InvalidLocationError(
                "Must provide location for WattNet provider"
            )
        location = location.upper()
        if location in WATTNET_ZONES:
            return location
        raise InvalidLocationError("WattNet only supports zone names (e.g GB)")