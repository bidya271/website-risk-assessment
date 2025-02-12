import whois

def get_whois_data(domain):
    try:
        domain_info = whois.whois(domain)

        # Structuring the output similar to check_https function
        return {
            "domain_name": domain_info.domain_name,
            "registrar": domain_info.registrar,
            "creation_date": str(domain_info.creation_date),
            "expiration_date": str(domain_info.expiration_date),
            "updated_date": str(domain_info.updated_date),
            "name_servers": domain_info.name_servers
        }
    except Exception as e:
        return {"error": f"Error retrieving WHOIS data: {e}"}

# Example usage
if __name__ == "__main__":
    domain = "gocloudgain.com"
    print(get_whois_data(domain))
