import requests
from confluent_kafka.avro import CachedSchemaRegistryClient


class CertificateAuthSchemaRegistryClient(CachedSchemaRegistryClient):
    """
    Extend the CachedSchemaRegistryClient to support certificate-based authentication.
    """
    def __init__(self, schema_registry_url, cert_path, key_path, ca_path):
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        super().__init__({"url": schema_registry_url})

    def _send_request(self, url, method="GET"):
        """
        Override _send_request to use certificates for HTTPS requests.
        """
        try:
            response = requests.request(
                method,
                url,
                cert=(self.cert_path, self.key_path),
                verify=self.ca_path,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")


# Configuration
SCHEMA_REGISTRY_URL = "https://your-schema-registry-url"  # Replace with your Schema Registry URL
CERTIFICATE_PATH = "/path/to/certificate.pem"  # Client certificate
PRIVATE_KEY_PATH = "/path/to/private_key.pem"  # Private key
CA_CERTIFICATE_PATH = "/path/to/ca_certificate.pem"  # CA certificate

# Initialize the client with certificate authentication
schema_registry_client = CertificateAuthSchemaRegistryClient(
    schema_registry_url=SCHEMA_REGISTRY_URL,
    cert_path=CERTIFICATE_PATH,
    key_path=PRIVATE_KEY_PATH,
    ca_path=CA_CERTIFICATE_PATH
)


def list_subjects():
    """
    List all subjects in the Schema Registry.
    """
    try:
        subjects = schema_registry_client.get_subjects()
        print(f"Subjects: {subjects}")
        return subjects
    except Exception as e:
        print(f"Error fetching subjects: {e}")


def get_latest_schema(subject):
    """
    Get the latest schema for a given subject.
    """
    try:
        schema_metadata = schema_registry_client.get_latest_schema(subject)
        print(f"Subject: {subject}")
        print(f"Schema ID: {schema_metadata[0]}")
        print(f"Schema Version: {schema_metadata[1]}")
        print(f"Schema: {schema_metadata[2].to_json()}")
        return schema_metadata
    except Exception as e:
        print(f"Error fetching schema for {subject}: {e}")


def main():
    # List all subjects
    subjects = list_subjects()
    if not subjects:
        print("No subjects found.")
        return

    # Fetch and display the latest schema for each subject
    for subject in subjects:
        get_latest_schema(subject)


if __name__ == "__main__":
    main()

