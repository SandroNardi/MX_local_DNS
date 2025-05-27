import os
import meraki
import json
import requests

API_KEY = os.getenv("MK_CSM_KEY")  # Fetch API key from environment variables

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
DISCLAIMER_MESSAGE = 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'


# Singleton-style global variable for the Meraki Dashboard API instance
_dashboard = None

# Cache for organizations and networks
_organizations_cache = None
_networks_cache = {}

# Global variable to store the selected organization ID
_selected_organization_id = None


def set_organization_id(organization_id):
    """
    Set the selected organization ID.

    :param organization_id: The ID of the organization to set.
    """
    global _selected_organization_id
    _selected_organization_id = organization_id
    logger.info(f"Organization ID set to: {_selected_organization_id}")


def get_organization_id():
    """
    Get the currently selected organization ID.

    :return: The currently selected organization ID.
    """
    global _selected_organization_id
    return _selected_organization_id


def _get_dashboard():
    """Get or create a singleton instance of the Meraki Dashboard API."""
    global _dashboard
    if _dashboard is None:
        _dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)
    return _dashboard


def _get_organizations():
    """
    Get the list of organizations, either from the cache or by making an API call.
    """
    global _organizations_cache
    if _organizations_cache is None:
        logger.info("Fetching organizations from the Meraki API...")
        dashboard = _get_dashboard()
        try:
            _organizations_cache = dashboard.organizations.getOrganizations()
        except Exception as e:
            logger.error(f"Error fetching organizations: {e}")
            _organizations_cache = (
                []
            )  # Ensure the cache is a list even if the call fails
    else:
        logger.info("Using cached organizations data.")
    return _organizations_cache


def _get_networks():
    """
    Get the list of networks for a specific organization, either from the cache or by making an API call.
    """
    global _networks_cache
    if _selected_organization_id not in _networks_cache:
        logger.info(
            f"Fetching networks for organization {_selected_organization_id} from the Meraki API..."
        )
        dashboard = _get_dashboard()
        try:
            _networks_cache[_selected_organization_id] = (
                dashboard.organizations.getOrganizationNetworks(
                    _selected_organization_id
                )
            )
        except Exception as e:
            logger.error(
                f"Error fetching networks for organization {_selected_organization_id}: {e}"
            )
            _networks_cache[_selected_organization_id] = (
                []
            )  # Ensure the cache is a list even if the call fails
    else:
        logger.info(
            f"Using cached networks data for organization {_selected_organization_id}."
        )
    return _networks_cache[_selected_organization_id]


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def make_request(method, endpoint, payload=None):
    """Utility function to handle API requests."""
    url = f"https://api.meraki.com/api/v1/organizations/{_selected_organization_id}/appliance/dns/local/{endpoint}"
    try:
        # Log the API request details
        logger.info(f"Making {method} request to {url}")
        if payload:
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")

        # Make the HTTP request
        response = requests.request(
            method, url, headers=HEADERS, data=json.dumps(payload) if payload else None
        )
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log and return the response
        if response.text.strip():
            logger.info(f"Response: {response.status_code} - {response.text}")
            return response.json()
        else:
            logger.info(f"Response: {response.status_code} - No content")
            return None

    except requests.exceptions.HTTPError as http_err:
        # Log HTTP errors with detailed information
        logger.error(f"HTTP error occurred: {http_err}")
        logger.error(
            f"Method: {method}, URL: {url}, Status Code: {response.status_code}, Response: {response.text}"
        )
        return {
            "error": "HTTPError",
            "details": response.text,
            "status_code": response.status_code,
        }

    except requests.exceptions.ConnectionError as conn_err:
        # Log connection errors
        logger.error(f"Connection error occurred: {conn_err}")
        logger.error(f"Method: {method}, URL: {url}")
        return {"error": "ConnectionError", "details": str(conn_err)}

    except requests.exceptions.Timeout as timeout_err:
        # Log timeout errors
        logger.error(f"Timeout error occurred: {timeout_err}")
        logger.error(f"Method: {method}, URL: {url}")
        return {"error": "TimeoutError", "details": str(timeout_err)}

    except requests.exceptions.RequestException as req_err:
        # Log general request errors
        logger.error(f"Request error occurred: {req_err}")
        logger.error(f"Method: {method}, URL: {url}")
        return {"error": "RequestException", "details": str(req_err)}


def get_organizations():
    """
    Fetch all organizations accessible via the API key using the Meraki Dashboard API.
    """
    response = _get_organizations()
    if response:
        # Transform response into a format suitable for put_datatable
        table_data = [
            {
                "ID": org.get("id"),
                "Name": org.get("name"),
                "URL": org.get("url"),
                "API Enabled": org.get("api", {}).get("enabled", False),
                "Licensing Model": org.get("licensing", {}).get("model"),
            }
            for org in response
        ]
        return table_data
    else:
        return []


def list_networks():
    """
    Fetch all networks associated with a specific organization.

    :param organization_id: The ID of the selected organization.
    :return: A list of networks in a format suitable for `put_datatable`.
    """
    response = _get_networks()
    if response:
        # Format response into a list of dictionaries
        table_data = [
            {
                "ID": network.get("id"),
                "Name": network.get("name"),
                "Type": network.get("type"),
                "Time Zone": network.get("timeZone"),
                "Tags": ", ".join(network.get("tags", [])),
            }
            for network in response
        ]
        return table_data
    else:
        return []


def list_profiles():
    """
    Fetch all profiles and include information about their associated networks.
    Use existing functions to retrieve network assignments and network names.
    If a profile is assigned to a network, display the network ID and name.
    If not, display [unassigned].
    """
    # Fetch profiles
    profiles_response = make_request("GET", "profiles")
    if not profiles_response or "items" not in profiles_response:
        return []

    # Fetch network assignments
    assignments = list_network_assignments()
    if not assignments:
        assignments = []

    # Fetch all networks for the organization
    networks = list_networks()
    network_map = (
        {network["ID"]: network["Name"] for network in networks} if networks else {}
    )

    # Map profile IDs to network information
    profile_to_network = {}
    for assignment in assignments:
        profile_id = assignment.get("Profile ID")
        network_id = assignment.get("Network ID")
        if profile_id and network_id:
            profile_to_network[profile_id] = {
                "Network ID": network_id,
                "Network Name": network_map.get(network_id, "[unknown]"),
            }

    # Format the profiles data for display
    table_data = []
    for profile in profiles_response["items"]:
        profile_id = profile.get("profileId")
        profile_name = profile.get("name")

        # Check if the profile is assigned to a network
        if profile_id in profile_to_network:
            network_info = profile_to_network[profile_id]
            table_data.append(
                {
                    "Profile ID": profile_id,
                    "Name": profile_name,
                    "Network ID": network_info.get("Network ID"),
                    "Network Name": network_info.get("Network Name"),
                }
            )
        else:
            table_data.append(
                {
                    "Profile ID": profile_id,
                    "Name": profile_name,
                    "Network ID": "[unassigned]",
                    "Network Name": "[unassigned]",
                }
            )
    return table_data


# 3. Create a new profile
def create_profile(profile_name):
    payload = {"name": profile_name}
    response = make_request("POST", "profiles", payload)
    if isinstance(response, dict) and "error" in response:
        return response
    else:
        return {
            "Profile ID": response.get("profileId"),
            "Name": response.get("name"),
        }


# 4. Delete a profile
def delete_profile(profile_id):
    response = make_request("DELETE", f"profiles/{profile_id}")
    return response


# 5. Create a new DNS record and assign it to a profile
def create_dns_record(profile_id, hostname, address):
    payload = {
        "hostname": hostname,
        "address": address,
        "profile": {"id": profile_id},
    }
    response = make_request("POST", "records", payload)
    return response


# 6. List all DNS records associated with a profile
def list_dns_records():
    response = make_request("GET", "records")
    if response and "items" in response:
        table_data = [
            {
                "Record ID": record.get("recordId"),
                "Hostname": record.get("hostname"),
                "Address": record.get("address"),
                "Profile ID": record.get("profile", {}).get("id"),
            }
            for record in response["items"]
        ]
        return table_data
    return []


# 7. Delete a DNS record in a profile
def delete_dns_record(record_id):
    response = make_request("DELETE", f"records/{record_id}")
    return response


# 8. Assign a profile to a network
def assign_profile_to_network(network_id, profile_id):
    payload = {
        "items": [
            {"network": {"id": network_id}, "profile": {"id": profile_id}},
        ]
    }
    response = make_request("POST", "profiles/assignments/bulkCreate", payload)
    return response


# 9. List all networks with the associated profile
def list_network_assignments():
    """
    Fetch all network assignments with additional information:
    - Network Name (matching the Network ID from _get_networks())
    - Profile Name (matching the Profile ID from make_request("GET", "profiles"))
    """
    # Fetch the list of networks for the organization
    networks = _get_networks()
    network_map = {network["id"]: network["name"] for network in networks}

    # Fetch the list of profiles for the organization
    profiles_response = make_request("GET", "profiles")
    profiles = profiles_response.get("items", []) if profiles_response else []
    profile_map = {profile["profileId"]: profile["name"] for profile in profiles}

    # Fetch the list of assignments
    response = make_request("GET", "profiles/assignments")
    if response and "items" in response:
        table_data = []
        for assignment in response["items"]:
            network_id = assignment.get("network", {}).get("id")
            profile_id = assignment.get("profile", {}).get("id")

            # Add network name and profile name using the cached maps
            table_data.append(
                {
                    "Assignment ID": assignment.get("assignmentId"),
                    "Network ID": network_id,
                    "Network Name": network_map.get(network_id, "[unknown]"),
                    "Profile ID": profile_id,
                    "Profile Name": profile_map.get(profile_id, "[unknown]"),
                }
            )
        return table_data
    return []


# 10. Remove the association between a profile and a network
def remove_network_assignment(assignment_id):
    payload = {"items": [{"assignmentId": assignment_id}]}
    response = make_request("POST", "profiles/assignments/bulkDelete", payload)
    return response


# Placeholder for the main function
def main():
    # Placeholder for PyWebIO interface
    # Future operations will be implemented here using PyWebIO
    pass


if __name__ == "__main__":
    main()
