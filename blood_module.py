
"""
Blood Donation Eligibility & Donor Matching System
Module containing:
- Parent class: Donor
- Subclass: RegularDonor (Inheritance)
- Function 1: calculate_next_eligible_date() - calculation
- Function 2: donation_decision() - decision-making
"""

from datetime import datetime, timedelta


# ============================================================
# BLOOD TYPE COMPATIBILITY MATRIX
# ============================================================
# Key   = Donor blood type
# Value = List of recipient blood types they can donate to
# ============================================================
BLOOD_COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # Universal donor
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],  # Universal recipient
}

VALID_BLOOD_TYPES = list(BLOOD_COMPATIBILITY.keys())


# ============================================================
# PARENT CLASS
# ============================================================
class Donor:
    """Represents a blood donor with 4 attributes."""

    def __init__(self, name, age, weight, blood_type, last_donation_date):
        self.name = name                          # attribute 1
        self.age = age                            # attribute 2
        self.weight = weight                      # attribute 3
        self.blood_type = blood_type.upper()      # attribute 4
        self.last_donation_date = last_donation_date  # attribute 5 (bonus)

    # ---------------- Method 1: Calculation ----------------
    def calculate_donation_interval(self):
        """Returns days since last donation."""
        if self.last_donation_date is None:
            return 0
        days = (datetime.now() - self.last_donation_date).days
        return max(days, 0)

    # ---------------- Method 2: Decision-making ----------------
    def eligibility_status(self):
        """Returns eligibility status based on medical rules."""
        days_since = self.calculate_donation_interval()

        # Age rule
        if self.age < 17:
            return "Ineligible", "Age below 17 years old."
        if self.age > 65:
            return "Ineligible", "Age above 65 years old."

        # Weight rule
        if self.weight < 45:
            return "Ineligible", "Weight below 45 kg."

        # Recent donation rule (90 days for whole blood)
        if days_since < 90:
            remaining = 90 - days_since
            return "Temporarily Deferred", f"Wait {remaining} more day(s). Minimum 90 days between donations."

        return "Eligible", "You are eligible to donate blood."

    def can_donate_to(self):
        """Returns list of blood types this donor can donate to."""
        return BLOOD_COMPATIBILITY.get(self.blood_type, [])

    def __str__(self):
        return f"{self.name} ({self.blood_type})"


# ============================================================
# SUBCLASS (INHERITANCE)
# ============================================================
class RegularDonor(Donor):
    """
    Subclass representing a regular/repeat donor.
    Adds loyalty bonus + priority matching + shorter wait period.
    """

    def __init__(self, name, age, weight, blood_type, last_donation_date, total_donations):
        super().__init__(name, age, weight, blood_type, last_donation_date)
        self.total_donations = total_donations    # NEW attribute

    # MODIFIED method — regular donors get 60-day interval instead of 90
    def eligibility_status(self):
        days_since = self.calculate_donation_interval()

        if self.age < 17:
            return "Ineligible", "Age below 17 years old."
        if self.age > 65:
            return "Ineligible", "Age above 65 years old."
        if self.weight < 45:
            return "Ineligible", "Weight below 45 kg."

        if days_since < 60:
            remaining = 60 - days_since
            return "Temporarily Deferred", f"Regular donor: wait {remaining} more day(s)."

        return "Eligible", f"Priority donor! {self.total_donations} previous donations."

    # NEW method — loyalty tier
    def loyalty_tier(self):
        if self.total_donations >= 20:
            return "🏆 Platinum Donor"
        elif self.total_donations >= 10:
            return "🥇 Gold Donor"
        elif self.total_donations >= 5:
            return "🥈 Silver Donor"
        return "🥉 Bronze Donor"


# ============================================================
# FUNCTION 1: Calculation / Data Processing
# ============================================================
def calculate_next_eligible_date(last_donation_date, interval_days=90):
    """
    Calculates the next eligible donation date.
    Returns a formatted string or 'Eligible Now'.
    """
    if last_donation_date is None:
        return "Eligible Now"

    next_date = last_donation_date + timedelta(days=interval_days)
    today = datetime.now()

    if next_date <= today:
        return "Eligible Now"
    return next_date.strftime("%d %B %Y")


# ============================================================
# FUNCTION 2: Decision-making / Result Generation
# ============================================================
def donation_decision(eligibility, recipient_type, donor_type):
    """
    Generates a final decision message for the donor.
    Combines eligibility + compatibility + donor tier.
    """
    status, reason = eligibility

    if status == "Eligible":
        if recipient_type in BLOOD_COMPATIBILITY.get(donor_type, []):
            return f"✅ MATCH FOUND! {donor_type} can donate to {recipient_type}. {reason}"
        else:
            return f"⚠️ Eligible, but {donor_type} is NOT compatible with {recipient_type}."
    elif status == "Temporarily Deferred":
        return f"⏳ Deferred: {reason}"
    else:
        return f"❌ Ineligible: {reason}"