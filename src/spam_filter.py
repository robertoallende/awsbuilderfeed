"""Spam detection module for AWS Builder articles."""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

from config import BASE_DIR


SPAM_RULES_FILE = BASE_DIR / "config" / "spam_rules.json"
SPAM_RULES_LOCAL_FILE = BASE_DIR / "config" / "spam_rules.local.json"


def load_rules() -> List[Dict[str, Any]]:
    """Load spam detection rules from config files.
    
    Loads main rules and optionally extends with local rules.
    """
    rules = []
    
    # Load main rules
    if SPAM_RULES_FILE.exists():
        with open(SPAM_RULES_FILE) as f:
            data = json.load(f)
            rules.extend(data.get("rules", []))
    
    # Load local rules (optional override/extension)
    if SPAM_RULES_LOCAL_FILE.exists():
        with open(SPAM_RULES_LOCAL_FILE) as f:
            data = json.load(f)
            rules.extend(data.get("rules", []))
    
    return [r for r in rules if r.get("enabled", True)]


def check_keyword_rule(article: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """Check if article matches keyword rule."""
    field = rule.get("field", "title")
    patterns = rule.get("patterns", [])
    case_sensitive = rule.get("case_sensitive", False)
    
    text = str(article.get(field, ""))
    if not case_sensitive:
        text = text.lower()
        patterns = [p.lower() for p in patterns]
    
    return any(pattern in text for pattern in patterns)


def check_regex_rule(article: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """Check if article matches regex rule."""
    field = rule.get("field", "title")
    pattern = rule.get("pattern", "")
    
    text = str(article.get(field, ""))
    try:
        return bool(re.search(pattern, text))
    except re.error:
        return False


def check_author_rule(article: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """Check if article author matches rule."""
    field = rule.get("field", "author_alias")
    patterns = rule.get("patterns", [])
    case_sensitive = rule.get("case_sensitive", False)
    
    author = str(article.get(field, ""))
    if not case_sensitive:
        author = author.lower()
        patterns = [p.lower() for p in patterns]
    
    return author in patterns


def check_spam(article: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Check if article is spam.
    
    Args:
        article: Article dict with title, author_alias, tags, etc.
    
    Returns:
        Tuple of (is_spam, matched_rule_ids)
    """
    rules = load_rules()
    matched_rules = []
    
    for rule in rules:
        rule_type = rule.get("type", "keyword")
        rule_id = rule.get("id", "unknown")
        
        matched = False
        if rule_type == "keyword":
            matched = check_keyword_rule(article, rule)
        elif rule_type == "regex":
            matched = check_regex_rule(article, rule)
        elif rule_type == "author":
            matched = check_author_rule(article, rule)
        
        if matched:
            matched_rules.append(rule_id)
    
    return (len(matched_rules) > 0, matched_rules)
