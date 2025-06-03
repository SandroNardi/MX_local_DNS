from pywebio import start_server
from pywebio.output import (
    put_buttons,
    put_text,
    put_datatable,
    put_markdown,
    clear,
    toast,
)
from pywebio.input import input_group, input, select, actions
import Local_DNS_logic as api_logic  # Assuming the logic functions are in `Local_DNS_app.py`

# Global variable to store the selected organization

selected_org_name = None  # Store the organization name for displaying in the UI


# UI Functions
def select_organization():
    """Display the organization selection menu."""
    global selected_org_name
    clear()

    # Fetch the list of organizations
    organizations = api_logic.get_organizations()
    if isinstance(organizations, dict) and "error" in organizations:
        toast(
            f"Error {organizations.get('status_code', 'Unknown')} - {organizations.get('error')}: {organizations.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not organizations:
        put_text("No organizations found.")
        return

    # Prepare dropdown options for organization selection
    organization_options = [
        {"label": f"[{org['ID']}] - {org['Name']}", "value": org["ID"]}
        for org in organizations
    ]

    # Prompt the user to select an organization
    org_data = input_group(
        "Select an Organization",
        [
            select("Organization", name="org_id", options=organization_options),
        ],
    )

    # Store the selected organization details
    api_logic.set_organization_id(org_data["org_id"])
    selected_org_name = next(
        org["Name"] for org in organizations if org["ID"] == org_data["org_id"]
    )

    main_menu()  # Navigate to the main menu for the selected organization


def main_menu():
    """Display the main menu for the selected organization."""
    clear()
    put_markdown(
        f"### Organization: {selected_org_name} (ID: {api_logic.get_organization_id()})"
    )
    put_buttons(
        [
            {
                "label": "Manage Profiles",
                "value": "profiles",
            },
            {
                "label": "Manage DNS Records",
                "value": "dns_records",
            },
            {
                "label": "Network Association",
                "value": "networks",
            },
            {"label": "Back to Organization Selection", "value": "back"},
        ],
        onclick=handle_main_menu_action,
    )


def handle_main_menu_action(action):
    """Handle actions from the main menu."""
    if action == "profiles":
        list_profiles()
    elif action == "dns_records":
        list_dns_records()
    elif action == "networks":
        list_network_assignments()
    elif action == "back":
        select_organization()


# ========== Profiles Management ==========
def list_profiles():
    """List all profiles with associated networks."""
    clear()
    profiles = api_logic.list_profiles()
    if isinstance(profiles, dict) and "error" in profiles:
        toast(
            f"Error {profiles.get('status_code', 'Unknown')} - {profiles.get('error')}: {profiles.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not profiles:
        put_text("No profiles found.")
    else:
        profiles_display = [
            {
                "Profile Name": profile["Name"],
                "Profile ID": profile["Profile ID"],
                "Network ID": profile.get("Network ID", "[unassigned]"),
                "Network Name": profile.get("Network Name", "[unassigned]"),
            }
            for profile in profiles
        ]
        put_markdown("### Profiles with Associated Networks")
        put_datatable(profiles_display)
    put_buttons(
        [
            {"label": "Create New Profile", "value": "create"},
            {"label": "Delete Profile", "value": "delete"},
            {"label": "Back to Main Menu", "value": "back"},
        ],
        onclick=handle_profiles_action,
    )


def handle_profiles_action(action):
    """Handle actions related to profiles."""
    if action == "create":
        create_profile_page()
    elif action == "delete":
        delete_profile_page()
    elif action == "back":
        main_menu()


def create_profile_page():
    """Open a new page to create a profile."""
    clear()
    put_markdown("### Create a New Profile")
    profile_data = input_group("Create Profile", [input("Profile Name", name="name")])
    if profile_data:
        response = api_logic.create_profile(profile_data["name"])
        if isinstance(response, dict) and "error" in response:
            toast(
                f"Error {response.get('status_code', 'Unknown')} - {response.get('error')}: {response.get('details')}",
                color="error",
                duration=0,
            )
            return

        toast("Profile created successfully!", color="success")
    put_buttons(
        [{"label": "Back to Profiles", "value": "back"}],
        onclick=lambda _: list_profiles(),
    )


def delete_profile_page():
    """Open a new page to delete a profile."""
    clear()
    put_markdown("### Delete a Profile")
    profiles = api_logic.list_profiles()
    if isinstance(profiles, dict) and "error" in profiles:
        toast(
            f"Error {profiles.get('status_code', 'Unknown')} - {profiles.get('error')}: {profiles.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not profiles:
        put_text("No profiles available to delete.")
        put_buttons(
            [{"label": "Back to Profiles", "value": "back"}],
            onclick=lambda _: list_profiles(),
        )
        return

    profile_options = [
        {
            "label": f"[{profile['Profile ID']}] - {profile['Name']}",
            "value": profile["Profile ID"],
        }
        for profile in profiles
    ]
    profile_to_delete = input_group(
        "Select a Profile to Delete",
        [
            select("Profile", name="profile_id", options=profile_options),
            actions(
                name="actions",
                buttons=[
                    {"label": "Delete", "value": "delete", "color": "danger"},
                    {"label": "Back", "value": "back"},
                ],
            ),
        ],
    )
    # Handle the action after the input group returns a result
    handle_delete_profile_action(
        profile_to_delete["actions"], profile_to_delete["profile_id"]
    )


def handle_delete_profile_action(action, profile_id):
    """Handle actions for the delete profile page."""
    if action == "delete":
        response = api_logic.delete_profile(profile_id)

        if isinstance(response, dict) and "error" in response:
            # Handle error response
            error_message = (
                f"Error {response.get('status_code', 'Unknown')} - "
                f"{response.get('error')}: {response.get('details')}"
            )
            toast(error_message, color="error", duration=0)
        else:
            # Handle successful deletion
            toast("Profile deleted successfully!", color="success")

        # Reload the profiles table after action
        list_profiles()

    elif action == "back":
        # Navigate back to the profiles table
        list_profiles()


"""
    if profile_to_delete:
        response = api_logic.delete_profile(profile_to_delete["profile_id"])
        if isinstance(response, dict) and "error" in response:
            toast(
                f"Error {response.get('status_code', 'Unknown')} - {response.get('error')}: {response.get('details')}",
                color="error",
                duration=0,
            )
        else:
            toast("Profile deleted successfully!", color="success")
    put_buttons(
        [{"label": "Back to Profiles", "value": "back"}],
        onclick=lambda _: list_profiles(),
    )
"""


# ========== DNS Records Management ==========
def list_dns_records():
    """List all DNS records with associated profiles."""
    clear()
    dns_records = api_logic.list_dns_records()
    if isinstance(dns_records, dict) and "error" in dns_records:
        toast(
            f"Error {dns_records.get('status_code', 'Unknown')} - {dns_records.get('error')}: {dns_records.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not dns_records:
        put_text("No DNS records found.")
    else:
        dns_display = [
            {
                "Hostname": record["Hostname"],
                "Address": record["Address"],
                "Profile ID": record["Profile ID"],
            }
            for record in dns_records
        ]
        put_markdown("### DNS Records with Associated Profiles")
        put_datatable(dns_display)
    put_buttons(
        [
            {"label": "Create New DNS Record", "value": "create"},
            {"label": "Delete DNS Record", "value": "delete"},
            {"label": "Back to Main Menu", "value": "back"},
        ],
        onclick=handle_dns_records_action,
    )


def handle_dns_records_action(action):
    """Handle actions related to DNS records."""
    if action == "create":
        create_dns_record_page()
    elif action == "delete":
        delete_dns_record_page()
    elif action == "back":
        main_menu()


def create_dns_record_page():
    """Open a new page to create a DNS record."""
    clear()
    put_markdown("### Create a New DNS Record")
    profiles = api_logic.list_profiles()
    if isinstance(profiles, dict) and "error" in profiles:
        toast(
            f"Error {profiles.get('status_code', 'Unknown')} - {profiles.get('error')}: {profiles.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not profiles:
        put_text("No profiles available. Please create a profile first.")
        put_buttons(
            [{"label": "Back to DNS Records", "value": "back"}],
            onclick=lambda _: list_dns_records(),
        )
        return

    profile_options = [
        {
            "label": f"[{profile['Profile ID']}] - {profile['Name']}",
            "value": profile["Profile ID"],
        }
        for profile in profiles
    ]

    record_data = input_group(
        "Create DNS Record",
        [
            input("Hostname", name="hostname"),
            input("Address", name="address"),
            select("Profile", name="profile_id", options=profile_options),
        ],
    )

    response = api_logic.create_dns_record(
        record_data["profile_id"], record_data["hostname"], record_data["address"]
    )
    if isinstance(response, dict) and "error" in response:
        toast(
            f"Error {response.get('status_code', 'Unknown')} - {response.get('error')}: {response.get('details')}",
            color="error",
            duration=0,
        )
        return

    toast("DNS record created successfully!", color="success")
    put_buttons(
        [{"label": "Back to DNS Records", "value": "back"}],
        onclick=lambda _: list_dns_records(),
    )


def delete_dns_record_page():
    """Open a new page to delete a DNS record."""
    clear()
    put_markdown("### Delete a DNS Record")
    dns_records = api_logic.list_dns_records()
    if isinstance(dns_records, dict) and "error" in dns_records:
        toast(
            f"Error {dns_records.get('status_code', 'Unknown')} - {dns_records.get('error')}: {dns_records.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not dns_records:
        put_text("No DNS records available to delete.")
        put_buttons(
            [{"label": "Back to DNS Records", "value": "back"}],
            onclick=lambda _: list_dns_records(),
        )
        return

    record_options = [
        {
            "label": f"[{record['Record ID']}] - {record['Hostname']}",
            "value": record["Record ID"],
        }
        for record in dns_records
    ]
    record_to_delete = input_group(
        "Select a DNS Record to Delete",
        [
            select("DNS Record", name="record_id", options=record_options),
            actions(
                name="actions",
                buttons=[
                    {"label": "Delete", "value": "delete", "color": "danger"},
                    {"label": "Back", "value": "back"},
                ],
            ),
        ],
    )
    # Handle the action after the input group returns a result
    handle_delete_dns_record_action(
        record_to_delete["actions"], record_to_delete["record_id"]
    )


def handle_delete_dns_record_action(action, record_id):
    """Handle actions for the delete DNS record page."""
    if action == "delete":
        response = api_logic.delete_dns_record(record_id)

        if isinstance(response, dict) and "error" in response:
            # Handle error response
            error_message = (
                f"Error {response.get('status_code', 'Unknown')} - "
                f"{response.get('error')}: {response.get('details')}"
            )
            toast(error_message, color="error", duration=0)
        else:
            # Handle successful deletion
            toast("DNS record deleted successfully!", color="success")

        # Reload the DNS records table after action
        list_dns_records()

    elif action == "back":
        # Navigate back to the DNS records table
        list_dns_records()


# ========== Network Assignments Management ==========
def list_network_assignments():
    """List all networks with associated profiles."""
    clear()
    assignments = api_logic.list_network_assignments()

    if isinstance(assignments, dict) and "error" in assignments:
        toast(
            f"Error {assignments.get('status_code', 'Unknown')} - {assignments.get('error')}: {assignments.get('details')}",
            color="error",
            duration=0,
        )
        return

    if assignments:
        assignments_display = [
            {
                "Assignment ID": assignment["Assignment ID"],
                "Network ID": assignment["Network ID"],
                "Network Name": assignment["Network Name"],
                "Profile Name": assignment["Profile Name"],
            }
            for assignment in assignments
        ]
        put_markdown("### Networks with Associated Profiles")
        put_datatable(assignments_display)
    else:
        put_text("No network assignments found.")

    put_buttons(
        [
            {"label": "Create Network Assignment", "value": "create"},
            {"label": "Delete Network Assignment", "value": "delete"},
            {"label": "Back to Main Menu", "value": "back"},
        ],
        onclick=handle_network_assignments_action,
    )


def handle_network_assignments_action(action):
    """Handle actions related to network assignments."""
    if action == "create":
        create_network_assignment_page()
    elif action == "delete":
        delete_network_assignment_page()
    elif action == "back":
        main_menu()


def create_network_assignment_page():
    """Open a new page to create a network assignment."""
    clear()
    put_markdown("### Create a New Network Assignment")
    profiles = api_logic.list_profiles()
    if isinstance(profiles, dict) and "error" in profiles:
        toast(
            f"Error {profiles.get('status_code', 'Unknown')} - {profiles.get('error')}: {profiles.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not profiles:
        put_text("No profiles available. Please create a profile first.")
        put_buttons(
            [{"label": "Back to Network Assignments", "value": "back"}],
            onclick=lambda _: list_network_assignments(),
        )
        return

    networks = api_logic.list_networks()
    if isinstance(networks, dict) and "error" in networks:
        toast(
            f"Error {networks.get('status_code', 'Unknown')} - {networks.get('error')}: {networks.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not networks:
        put_text(
            "No networks available in this organization. Cannot create an assignment."
        )
        put_buttons(
            [{"label": "Back to Network Assignments", "value": "back"}],
            onclick=lambda _: list_network_assignments(),
        )
        return

    profile_options = [
        {
            "label": f"[{profile['Profile ID']}] - {profile['Name']}",
            "value": profile["Profile ID"],
        }
        for profile in profiles
    ]
    network_options = [
        {"label": f"[{network['ID']}] - {network['Name']}", "value": network["ID"]}
        for network in networks
    ]

    assignment_data = input_group(
        "Create Network Assignment",
        [
            select("Profile", name="profile_id", options=profile_options),
            select("Network", name="network_id", options=network_options),
        ],
    )

    response = api_logic.assign_profile_to_network(
        assignment_data["network_id"], assignment_data["profile_id"]
    )
    if isinstance(response, dict) and "error" in response:
        toast(
            f"Error {response.get('status_code', 'Unknown')} - {response.get('error')}: {response.get('details')}",
            color="error",
            duration=0,
        )
        put_buttons(
            [{"label": "Back to Network Assignments", "value": "back"}],
            onclick=lambda _: list_network_assignments(),
        )
        return

    toast("Network assignment created successfully!", color="success")
    put_buttons(
        [{"label": "Back to Network Assignments", "value": "back"}],
        onclick=lambda _: list_network_assignments(),
    )


def delete_network_assignment_page():
    """Open a new page to delete a network assignment."""
    clear()
    put_markdown("### Delete a Network Assignment")
    assignments = api_logic.list_network_assignments()
    if isinstance(assignments, dict) and "error" in assignments:
        toast(
            f"Error {assignments.get('status_code', 'Unknown')} - {assignments.get('error')}: {assignments.get('details')}",
            color="error",
            duration=0,
        )
        return

    if not assignments:
        put_text("No network assignments available to delete.")
        put_buttons(
            [{"label": "Back to Network Assignments", "value": "back"}],
            onclick=lambda _: list_network_assignments(),
        )
        return

    assignment_options = [
        {
            "label": f"[{assignment['Assignment ID']}] - Network: {assignment['Network ID']}-{assignment['Network Name']} - Profile: {assignment['Profile ID']}-{assignment['Profile Name']}",
            "value": assignment["Assignment ID"],
        }
        for assignment in assignments
    ]

    assignment_to_delete = input_group(
        "Select a Network Assignment to Delete",
        [
            select(
                "Network Assignment", name="assignment_id", options=assignment_options
            ),
            actions(
                name="actions",
                buttons=[
                    {"label": "Delete", "value": "delete", "color": "danger"},
                    {"label": "Back", "value": "back"},
                ],
            ),
        ],
    )
    # Handle the action after the input group returns a result
    handle_delete_network_assignment_action(
        assignment_to_delete["actions"], assignment_to_delete["assignment_id"]
    )


def handle_delete_network_assignment_action(action, assignment_id):
    """Handle actions for the delete network assignment page."""
    if action == "delete":
        response = api_logic.remove_network_assignment(assignment_id)

        if isinstance(response, dict) and "error" in response:
            # Handle error response
            error_message = (
                f"Error {response.get('status_code', 'Unknown')} - "
                f"{response.get('error')}: {response.get('details')}"
            )
            toast(error_message, color="error", duration=0)
        else:
            # Handle successful deletion
            toast("Network assignment deleted successfully!", color="success")

        # Reload the network assignments table after action
        list_network_assignments()

    elif action == "back":
        # Navigate back to the network assignments table
        list_network_assignments()


# Main Function to Start the PyWebIO App
def main():
    """Start the PyWebIO application."""
    select_organization()


def disclaimer():
    put_markdown("## MX Local DNS - Proof of concept")
    put_text(api_logic.DISCLAIMER_MESSAGE)
    put_text(
        "Please acknowledge the above to proccede",
    )
    user_action = actions(
        buttons=[
            {"label": "I Acknowledge", "value": "ack"},
        ],
    )
    if user_action == "ack":
        main()


if __name__ == "__main__":
    start_server(disclaimer, port=8080)
