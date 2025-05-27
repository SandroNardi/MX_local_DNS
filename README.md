# Local DNS Service on MX - GUI Implementation

## Overview

This project implements a graphical user interface (GUI) for managing the Local DNS Service on Cisco Meraki MX appliances. The GUI is built using the **PyWebIO** library and leverages the **Meraki Dashboard API** to create and manage Local DNS profiles, DNS records, and their assignments to networks.

The Local DNS Service enables DNS queries to be resolved locally on the MX appliance, which is particularly useful for environments where both public and internal DNS resolution are required.

## Features

- **Organization Selection**: Browse and select organizations accessible via the API key.
- **Profile Management**:
  - Create, list, and delete Local DNS profiles.
  - View associated networks for each profile.
- **DNS Record Management**:
  - Create, list, and delete DNS records.
  - Associate DNS records with Local DNS profiles.
- **Network Assignments**:
  - Assign Local DNS profiles to networks.
  - List and delete network assignments.
- **Error Handling**: Comprehensive error messages for API errors and failed operations.
- **Caching**: Optimized API calls with caching for organizations and networks.

## Prerequisites

To use this GUI and the Local DNS Service on MX, ensure the following:

- **MX Firmware Version**: The MX must be running firmware **19.1+**.
- **DHCP Settings**: The DNS nameserver setting under **DHCP Settings** must be configured to `Proxy to Upstream DNS`.
- **API Key**: A valid Meraki Dashboard API key is required, and it must have the appropriate permissions for the desired organization.

## API Configuration (Requires Firmware 19.1+)

The Local DNS Service on MX is only configurable via the Meraki Dashboard API. This GUI simplifies the process by providing an intuitive interface for the following:

### Create Local DNS Profile

Allows users to create DNS profiles for local DNS resolution. Profiles can be assigned to specific networks in the organization.

**API Documentation**:  
[Create Local DNS Profile](https://developer.cisco.com/meraki/api-v1/create-organization-appliance-dns-local-profile/)

---

### Create Local DNS Records

Users can create individual DNS records (hostname and IP address mappings) and associate them with specific profiles.

**API Documentation**:  
[Create Local DNS Records](https://developer.cisco.com/meraki/api-v1/create-organization-appliance-dns-local-record/)

---

### Assign Local DNS Profile to a Network

Profiles can be assigned to networks to enable local DNS resolution for specific domains and records.

**API Documentation**:  
[Bulk Create Local DNS Profile Assignments](https://developer.cisco.com/meraki/api-v1/bulk-organization-appliance-dns-local-profiles-assignments-create/)

---

### Local DNS Record Limit

**Note**: A maximum of **1024 local DNS records** can be configured per MX device.

---

## GUI Functionality

### Organization Management

- The GUI displays all accessible organizations associated with the provided API key.
- Users can select an organization to manage its Local DNS settings.

---

### Profile Management

- **List Profiles**: View all Local DNS profiles in the selected organization, including their names and associated networks.
- **Create Profile**: Add a new Local DNS profile to the selected organization.
- **Delete Profile**: Remove an existing Local DNS profile.

---

### DNS Records Management

- **List DNS Records**: View all configured DNS records and their associated profiles.
- **Create DNS Record**: Add a new DNS record (hostname and IP address mapping) to a Local DNS profile.
- **Delete DNS Record**: Remove an existing DNS record.

---

### Network Assignments

- **List Network Assignments**: View all network-to-profile assignments, including details about the network and profile.
- **Create Assignment**: Assign a Local DNS profile to a network.
- **Delete Assignment**: Remove an existing assignment between a network and a profile.

---

## DNote

The Local DNS Service on MX is only configurable via API at this time. The GUI implementation relies on API calls and requires proper configuration and permissions.

---

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. **Install Dependencies**:
   Use the following command to install the required libraries:

```bash
pip install meraki pywebio requests
```

3. **Set Environment Variables**:
   Add your Meraki Dashboard API key as an environment variable:

```bash
MK_CSM_KEY="your_api_key"
```

4. **Run the Application**:
   Start the GUI by running:

```bash

python Local_DNS_APP.py
```

5. **Access the GUI**:
   Open a browser and navigate to:

```
http://localhost:8080
```

---

## Additional Notes

- **Error Handling**: The GUI includes detailed error messages for failed API calls, including HTTP status codes and error details.
- **Caching**: Organizations and networks are cached to minimize API calls and improve performance.
- **License**: This project is released under an open-source license. See the LICENSE file for more details.

For more information, refer to the official Cisco Meraki documentation:
[Local DNS Service on MX](https://documentation.meraki.com/MX/Local_DNS_Service_on_MX).
