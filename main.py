
import streamlit as st
from datetime import datetime
from blood_module import (
    Donor,
    RegularDonor,
    calculate_next_eligible_date,
    donation_decision,
    VALID_BLOOD_TYPES,
)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Blood Donation System",
    page_icon="🩸",
    layout="centered",
)

st.title("🩸 Blood Donation Eligibility & Donor Matching System")
st.markdown("Check your eligibility and find compatible recipients instantly.")
st.divider()

# ============================================================
# USER INPUTS  (≥ 3 inputs)
# ============================================================
st.subheader("👤 Donor Information")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Full Name *")                         # INPUT 1
    age = st.number_input("Age (years) *", min_value=0, max_value=120, step=1)  # INPUT 2
    weight = st.number_input("Weight (kg) *", min_value=0.0, max_value=300.0, step=0.5)  # INPUT 3

with col2:
    blood_type = st.selectbox("Blood Type *", VALID_BLOOD_TYPES)  # INPUT 4
    donor_type = st.radio("Donor Type *", ["New Donor", "Regular Donor"])  # INPUT 5

# Regular donor extra input
total_donations = 0
if donor_type == "Regular Donor":
    total_donations = st.slider("Total Previous Donations", 1, 50, 5)  # INPUT 6

# Last donation date
has_donated = st.checkbox("Have you donated before?")
last_donation_date = None
if has_donated:
    last_donation_date = st.date_input(
        "Date of Last Donation",
        value=datetime.now(),
        max_value=datetime.now(),
    )

st.divider()

# ============================================================
# RECIPIENT (for matching)
# ============================================================
st.subheader("🎯 Recipient Matching")
recipient_type = st.selectbox("Recipient's Blood Type (for matching)", VALID_BLOOD_TYPES)

st.divider()

# ============================================================
# BUTTON TRIGGER
# ============================================================
if st.button("🔍 Check Eligibility & Match", use_container_width=True):
    try:
        # ---------- EXCEPTION HANDLING ----------

        # ERROR 1: Empty name field
        if not name.strip():
            st.error("❌ Error: Full Name cannot be empty.")

        # ERROR 2: Numerical validation
        elif age <= 0 or age > 120:
            st.error("❌ Error: Please enter a valid age (1–120).")
        elif weight <= 0:
            st.error("❌ Error: Weight must be greater than 0.")

        # ERROR 3: Logical validation
        elif weight < 45 and age < 17:
            st.error("❌ Error: Donor fails multiple eligibility criteria.")

        else:
            # Convert date if provided
            donation_date = None
            if has_donated and last_donation_date:
                donation_date = datetime.combine(last_donation_date, datetime.min.time())

            # ---------- OBJECT INSTANTIATION ----------
            if donor_type == "Regular Donor":
                donor = RegularDonor(
                    name=name.strip(),
                    age=age,
                    weight=weight,
                    blood_type=blood_type,
                    last_donation_date=donation_date,
                    total_donations=total_donations,
                )
            else:
                donor = Donor(
                    name=name.strip(),
                    age=age,
                    weight=weight,
                    blood_type=blood_type,
                    last_donation_date=donation_date,
                )

            # ---------- PROCESSING ----------
            eligibility = donor.eligibility_status()
            days_since = donor.calculate_donation_interval()
            compatible_list = donor.can_donate_to()

            interval = 60 if donor_type == "Regular Donor" else 90
            next_date = calculate_next_eligible_date(donation_date, interval)
            decision_msg = donation_decision(eligibility, recipient_type, donor.blood_type)

            # ---------- OUTPUT ----------
            st.subheader("📊 Results")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("Donor Name", donor.name)
                st.metric("Blood Type", donor.blood_type)
            with c2:
                st.metric("Days Since Last Donation", days_since)
                st.metric("Next Eligible Date", next_date)

            # Eligibility box
            status, reason = eligibility
            if status == "Eligible":
                st.success(f"✅ Status: {status} — {reason}")
            elif status == "Temporarily Deferred":
                st.warning(f"⏳ Status: {status} — {reason}")
            else:
                st.error(f"❌ Status: {status} — {reason}")

            # Loyalty tier (subclass-specific)
            if isinstance(donor, RegularDonor):
                st.info(f"Loyalty Tier: {donor.loyalty_tier()}")

            # Compatibility
            st.markdown("### 🧬 Blood Compatibility")
            st.write(f"**{donor.blood_type}** can donate to:")
            st.write(", ".join(compatible_list))

            # Final decision
            st.markdown("### 🩺 Final Decision")
            st.info(decision_msg)

            # Progress bar for wait time
            if status == "Temporarily Deferred":
                progress = min(days_since / interval, 1.0)
                st.progress(progress, text=f"Wait progress: {days_since}/{interval} days")

    # ---------- UNEXPECTED ERROR ----------
    except ValueError:
        st.error("❌ Error: Invalid input format. Please enter numbers correctly.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")

st.divider()
st.caption("DFK50083 Python Programming — Problem Based Assignment | Blood Donation System")