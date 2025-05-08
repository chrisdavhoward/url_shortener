
def is_spam_url(url):
    """
    Check if a URL appears to be spam based on some basic rules.
    Returns (is_spam, reason) tuple.
    """
    # Convert to lowercase for case-insensitive matching
    url_lower = url.lower()
    
    # List of spam keywords
    spam_keywords = [
        'casino', 'poker', 'viagra', 'cialis', 'sex', 'xxx',
        'porn', 'bet', 'lottery', 'free-money', 'make-money-fast',
        'get-rich', 'pharma', 'meds', 'pills', 'prescription'
    ]
    
    # Check for spam keywords in URL
    for keyword in spam_keywords:
        if keyword in url_lower:
            return True, f"URL contains blocked keyword: {keyword}"
    
    # Check for suspicious TLDs
    suspicious_tlds = ['.xyz', '.top', '.win', '.loan', '.online']
    for tld in suspicious_tlds:
        if url_lower.endswith(tld):
            return True, f"URL uses suspicious TLD: {tld}"
    
    # Check for excessive number of subdomains (potential phishing)
    domain_part = url_lower.split('://', 1)[-1].split('/', 1)[0]
    if domain_part.count('.') > 3:
        return True, "URL contains excessive subdomains"
    
    # Check for extremely long URLs (often spam or malicious)
    if len(url) > 1000:
        return True, "URL is suspiciously long"
    
    # Not detected as spam
    return False, None